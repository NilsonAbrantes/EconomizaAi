import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CadastroUsuarioForm, LoginForm
from .models import ItemFinanceiro, RegistroMensal


def login_view(request):
    if request.user.is_authenticated:
        return redirect("financas:novo")

    next_url = request.POST.get("next") or request.GET.get("next", "")
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].strip().lower()
        senha = form.cleaned_data["senha"]
        usuario = authenticate(request, username=email, password=senha)

        if usuario is not None and usuario.is_active:
            login(request, usuario)
            messages.success(request, "Login realizado com sucesso.")

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect("financas:novo")

        form.add_error(None, "E-mail ou senha inválidos.")

    return render(
        request,
        "financas/login.html",
        {"form": form, "next": next_url},
    )


def cadastro_view(request):
    if request.user.is_authenticated:
        return redirect("financas:novo")

    form = CadastroUsuarioForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            usuario = form.save()
        except IntegrityError:
            form.add_error("email", "Já existe uma conta com este e-mail.")
        else:
            login(request, usuario)
            messages.success(request, "Conta criada com sucesso. Bem-vindo!")
            return redirect("financas:novo")

    return render(
        request,
        "financas/cadastro.html",
        {"form": form},
    )


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "Você saiu da sua conta.")
    return redirect("financas:login")


def moeda_para_decimal(valor):
    if valor is None:
        return None

    texto = str(valor).strip()
    if not texto:
        return None

    texto = (
        texto.replace("R$", "")
        .replace(" ", "")
        .replace(".", "")
        .replace(",", ".")
    )

    try:
        numero = Decimal(texto)
        if numero < 0:
            return None
        return numero.quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def coletar_itens_post(request, prefixo, tipo):
    nomes = request.POST.getlist(f"{prefixo}_nome[]")
    valores = request.POST.getlist(f"{prefixo}_valor[]")

    itens = []

    for nome, valor in zip(nomes, valores):
        nome = nome.strip()
        valor_decimal = moeda_para_decimal(valor)

        if not nome and valor_decimal is None:
            continue

        if not nome or valor_decimal is None:
            raise ValueError(f"Preencha nome e valor corretamente em {tipo}.")

        itens.append({
            "tipo": tipo,
            "nome": nome,
            "valor": valor_decimal,
        })

    return itens


def calcular_situacao(salario, contas, faturas, gastos, bicos):
    total_contas = sum((item["valor"] for item in contas), Decimal("0.00"))
    total_faturas = sum((item["valor"] for item in faturas), Decimal("0.00"))
    total_gastos_extras = sum(
        (item["valor"] for item in gastos),
        Decimal("0.00"),
    )
    total_bicos = sum((item["valor"] for item in bicos), Decimal("0.00"))

    renda_total = salario + total_bicos
    total_gastos = total_contas + total_faturas + total_gastos_extras
    saldo_final = renda_total - total_gastos
    recomendacao_guardar = renda_total * Decimal("0.20")

    percentual_gasto = Decimal("0.00")
    percentual_saldo = Decimal("0.00")

    if renda_total > 0:
        percentual_gasto = total_gastos / renda_total
        percentual_saldo = saldo_final / renda_total

    if percentual_gasto >= Decimal("0.85") or saldo_final < 0:
        nivel = "Crítico"
        mensagem = (
            "Seus gastos estão muito altos em relação à renda. "
            "Revise contas fixas, reduza faturas e evite novas dívidas."
        )
    elif percentual_gasto >= Decimal("0.60"):
        nivel = "Moderado"
        mensagem = (
            "Sua situação exige atenção. Ainda existe saldo, mas os gastos "
            "comprometem uma parte importante da renda."
        )
    else:
        nivel = "Suave"
        mensagem = (
            "Sua situação está confortável. Você possui boa margem para guardar "
            "dinheiro, criar reserva de emergência ou investir em metas."
        )

    return {
        "total_contas": total_contas.quantize(Decimal("0.01")),
        "total_faturas": total_faturas.quantize(Decimal("0.01")),
        "total_gastos_extras": total_gastos_extras.quantize(Decimal("0.01")),
        "total_bicos": total_bicos.quantize(Decimal("0.01")),
        "renda_total": renda_total.quantize(Decimal("0.01")),
        "total_gastos": total_gastos.quantize(Decimal("0.01")),
        "saldo_final": saldo_final.quantize(Decimal("0.01")),
        "recomendacao_guardar": recomendacao_guardar.quantize(Decimal("0.01")),
        "percentual_gasto": percentual_gasto,
        "percentual_saldo": percentual_saldo,
        "nivel": nivel,
        "mensagem": mensagem,
    }


def processar_registro(request, registro=None):
    mes = request.POST.get("mes")
    ano = request.POST.get("ano")
    salario = moeda_para_decimal(request.POST.get("salario"))

    if not mes or not ano:
        raise ValueError("Informe mês e ano.")

    try:
        mes = int(mes)
        ano = int(ano)
    except ValueError as erro:
        raise ValueError("Mês e ano precisam ser válidos.") from erro

    if mes < 1 or mes > 12:
        raise ValueError("Informe um mês válido.")

    if ano < 1900 or ano > 3000:
        raise ValueError("Informe um ano válido.")

    if salario is None or salario <= 0:
        raise ValueError("Informe um salário válido.")

    contas = coletar_itens_post(request, "conta", ItemFinanceiro.TIPO_CONTA)
    faturas = coletar_itens_post(request, "fatura", ItemFinanceiro.TIPO_FATURA)
    gastos = coletar_itens_post(request, "gasto", ItemFinanceiro.TIPO_GASTO)
    bicos = coletar_itens_post(request, "bico", ItemFinanceiro.TIPO_bico)

    calculo = calcular_situacao(salario, contas, faturas, gastos, bicos)

    with transaction.atomic():
        if registro:
            registro.usuario = request.user
            registro.mes = mes
            registro.ano = ano
            registro.salario = salario
            registro.total_contas = calculo["total_contas"]
            registro.total_faturas = calculo["total_faturas"]
            registro.total_gastos_extras = calculo["total_gastos_extras"]
            registro.total_bicos = calculo["total_bicos"]
            registro.renda_total = calculo["renda_total"]
            registro.total_gastos = calculo["total_gastos"]
            registro.saldo_final = calculo["saldo_final"]
            registro.recomendacao_guardar = calculo["recomendacao_guardar"]
            registro.nivel = calculo["nivel"]
            registro.mensagem = calculo["mensagem"]
            registro.save()
            registro.itens.all().delete()
        else:
            registro, _ = RegistroMensal.objects.update_or_create(
                usuario=request.user,
                mes=mes,
                ano=ano,
                defaults={
                    "salario": salario,
                    "total_contas": calculo["total_contas"],
                    "total_faturas": calculo["total_faturas"],
                    "total_gastos_extras": calculo["total_gastos_extras"],
                    "total_bicos": calculo["total_bicos"],
                    "renda_total": calculo["renda_total"],
                    "total_gastos": calculo["total_gastos"],
                    "saldo_final": calculo["saldo_final"],
                    "recomendacao_guardar": calculo["recomendacao_guardar"],
                    "nivel": calculo["nivel"],
                    "mensagem": calculo["mensagem"],
                },
            )
            registro.itens.all().delete()

        todos_itens = contas + faturas + gastos + bicos

        ItemFinanceiro.objects.bulk_create([
            ItemFinanceiro(
                registro=registro,
                tipo=item["tipo"],
                nome=item["nome"],
                valor=item["valor"],
            )
            for item in todos_itens
        ])

    return registro


@login_required
def novo_registro(request):
    hoje = datetime.now()

    if request.method == "POST":
        try:
            registro = processar_registro(request)
            messages.success(request, "Mês salvo com sucesso no banco de dados.")
            return redirect("financas:detalhes", pk=registro.pk)
        except ValueError as erro:
            messages.error(request, str(erro))
        except IntegrityError:
            messages.error(request, "Já existe um registro com esse mês e ano.")

    context = {
        "titulo_pagina": "Novo lançamento mensal",
        "modo": "novo",
        "mes_atual": hoje.month,
        "ano_atual": hoje.year,
        "registro": None,
        "contas": [],
        "faturas": [],
        "gastos": [],
        "bicos": [],
    }
    return render(request, "financas/form.html", context)


@login_required
def editar_registro(request, pk):
    registro = get_object_or_404(
        RegistroMensal,
        pk=pk,
        usuario=request.user,
    )

    if request.method == "POST":
        try:
            registro = processar_registro(request, registro=registro)
            messages.success(request, "Registro atualizado com sucesso.")
            return redirect("financas:detalhes", pk=registro.pk)
        except ValueError as erro:
            messages.error(request, str(erro))
        except IntegrityError:
            messages.error(request, "Já existe outro registro com esse mês e ano.")

    context = {
        "titulo_pagina": "Editar lançamento mensal",
        "modo": "editar",
        "registro": registro,
        "mes_atual": registro.mes,
        "ano_atual": registro.ano,
        "contas": registro.itens.filter(tipo=ItemFinanceiro.TIPO_CONTA),
        "faturas": registro.itens.filter(tipo=ItemFinanceiro.TIPO_FATURA),
        "gastos": registro.itens.filter(tipo=ItemFinanceiro.TIPO_GASTO),
        "bicos": registro.itens.filter(tipo=ItemFinanceiro.TIPO_bico),
    }
    return render(request, "financas/form.html", context)


@login_required
def historico(request):
    busca = request.GET.get("busca", "").strip()
    registros = RegistroMensal.objects.filter(usuario=request.user)

    if busca:
        registros = registros.filter(
            Q(nivel__icontains=busca)
            | Q(ano__icontains=busca)
            | Q(mes__icontains=busca)
        )

    context = {
        "registros": registros,
        "busca": busca,
    }
    return render(request, "financas/historico.html", context)


@login_required
def detalhes_registro(request, pk):
    registro = get_object_or_404(
        RegistroMensal,
        pk=pk,
        usuario=request.user,
    )

    context = {
        "registro": registro,
        "contas": registro.itens.filter(tipo=ItemFinanceiro.TIPO_CONTA),
        "faturas": registro.itens.filter(tipo=ItemFinanceiro.TIPO_FATURA),
        "gastos": registro.itens.filter(tipo=ItemFinanceiro.TIPO_GASTO),
        "bicos": registro.itens.filter(tipo=ItemFinanceiro.TIPO_bico),
    }
    return render(request, "financas/detalhes.html", context)


@login_required
@require_POST
def excluir_registro(request, pk):
    registro = get_object_or_404(
        RegistroMensal,
        pk=pk,
        usuario=request.user,
    )
    registro.delete()
    messages.success(request, "Registro excluído com sucesso.")
    return redirect("financas:historico")


@login_required
def exportar_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="historico_financeiro.csv"'
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    writer.writerow([
        "Mês",
        "Ano",
        "Salário",
        "Contas fixas",
        "Faturas",
        "Gastos extras",
        "Rendas extras",
        "Renda total",
        "Total de gastos",
        "Saldo final",
        "Recomendação para guardar",
        "Nível",
        "Atualizado em",
    ])

    registros = RegistroMensal.objects.filter(usuario=request.user)

    for registro in registros:
        writer.writerow([
            registro.get_mes_display(),
            registro.ano,
            registro.salario,
            registro.total_contas,
            registro.total_faturas,
            registro.total_gastos_extras,
            registro.total_bicos,
            registro.renda_total,
            registro.total_gastos,
            registro.saldo_final,
            registro.recomendacao_guardar,
            registro.nivel,
            registro.atualizado_em.strftime("%d/%m/%Y %H:%M"),
        ])

    return response
