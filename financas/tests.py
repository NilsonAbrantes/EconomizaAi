from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import RegistroMensal


User = get_user_model()


class AutenticacaoEIsolamentoTests(TestCase):
    def setUp(self):
        self.usuario_a = User.objects.create_user(
            username="usuario-a@example.com",
            email="usuario-a@example.com",
            first_name="Usuário A",
            password="SenhaSegura123!",
        )
        self.usuario_b = User.objects.create_user(
            username="usuario-b@example.com",
            email="usuario-b@example.com",
            first_name="Usuário B",
            password="SenhaSegura123!",
        )
        self.registro_a = RegistroMensal.objects.create(
            usuario=self.usuario_a,
            mes=1,
            ano=2026,
            salario=Decimal("3000.00"),
        )
        self.registro_b = RegistroMensal.objects.create(
            usuario=self.usuario_b,
            mes=1,
            ano=2026,
            salario=Decimal("4500.00"),
        )

    def test_usuario_nao_autenticado_e_redirecionado_para_login(self):
        resposta = self.client.get(reverse("financas:historico"))
        self.assertRedirects(
            resposta,
            f"{reverse('financas:login')}?next={reverse('financas:historico')}",
        )

    def test_historico_exibe_somente_registros_do_usuario(self):
        self.client.force_login(self.usuario_a)
        resposta = self.client.get(reverse("financas:historico"))

        self.assertContains(resposta, "R$ 3000.00")
        self.assertNotContains(resposta, "R$ 4500.00")

    def test_usuario_nao_acessa_registro_de_outra_conta(self):
        self.client.force_login(self.usuario_a)
        resposta = self.client.get(
            reverse(
                "financas:detalhes",
                kwargs={"pk": self.registro_b.pk},
            )
        )
        self.assertEqual(resposta.status_code, 404)

    def test_senha_de_usuario_e_armazenada_com_hash(self):
        self.assertNotEqual(self.usuario_a.password, "SenhaSegura123!")
        self.assertTrue(self.usuario_a.check_password("SenhaSegura123!"))
