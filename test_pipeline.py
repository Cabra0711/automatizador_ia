"""
Pruebas Unitarias Automatizadas - Talento Andino S.A.S.
Misión 5: Calidad del Software con pytest

Pruebas incluidas:
1. Cálculo de días hábiles excluyendo fines de semana y festivos oficiales colombianos.
2. Enmascaramiento de datos personales sensibles (Cédulas, Celulares, Correos).
3. Reglas de revisión humana (Saldo insuficiente, Vacaciones sin fechas, Empleado inexistente, Confianza baja).
4. Limpieza de datos (Deduplicación, normalización de correo y áreas vacías).
"""

import pytest
from mision2_festivos import calcular_dias_habiles, obtener_festivos
from mision3_ia import (
    enmascarar_datos_personales,
    evaluar_reglas_revision,
    validar_json_ia
)


# ==============================================================================
# 1. PRUEBAS DE CÁLCULO DE DÍAS HÁBILES (MISIÓN 2)
# ==============================================================================
class TestDiasHabiles:
    @pytest.fixture
    def festivos_colombia(self):
        # Obtiene festivos de Nager.Date o respaldo local
        return obtener_festivos()

    def test_caso_s01_cinco_dias_habiles(self, festivos_colombia):
        """S01: 14 al 18 de diciembre de 2026 = 5 días hábiles (Lunes a Viernes)."""
        dias = calcular_dias_habiles("2026-12-14", "2026-12-18", festivos_colombia)
        assert dias == 5

    def test_caso_s05_cuatro_dias_por_festivo(self, festivos_colombia):
        """S05: 7 al 11 de diciembre de 2026 = 4 días hábiles (el 8 dic es festivo)."""
        dias = calcular_dias_habiles("2026-12-07", "2026-12-11", festivos_colombia)
        assert dias == 4

    def test_caso_s06_ocho_dias_por_festivo_navidad(self, festivos_colombia):
        """S06: 21 al 31 de diciembre de 2026 = 8 días hábiles (el 25 dic es festivo)."""
        dias = calcular_dias_habiles("2026-12-21", "2026-12-31", festivos_colombia)
        assert dias == 8

    def test_fechas_invalidas_o_fin_menor_inicio(self, festivos_colombia):
        """Si la fecha de fin es anterior al inicio o faltan fechas, debe retornar 0."""
        assert calcular_dias_habiles("2026-12-20", "2026-12-10", festivos_colombia) == 0
        assert calcular_dias_habiles(None, "2026-12-10", festivos_colombia) == 0
        assert calcular_dias_habiles("", "", festivos_colombia) == 0

    def test_solo_fin_de_semana(self, festivos_colombia):
        """Un fin de semana (sábado y domingo) debe dar 0 días hábiles."""
        # 12 y 13 de diciembre de 2026 son sábado y domingo
        assert calcular_dias_habiles("2026-12-12", "2026-12-13", festivos_colombia) == 0


# ==============================================================================
# 2. PRUEBAS DE ENMASCARAMIENTO DE DATOS SENSIBLES (MISIÓN 3)
# ==============================================================================
class TestEnmascaramientoDatos:
    def test_enmascarar_cedula_documento(self):
        """Enmascara números de cédula sin alterar años de calendario."""
        texto = "Buenas, mi cédula es 1067890123 para el trámite de 2026."
        enmascarado = enmascarar_datos_personales(texto)
        assert "1067890123" not in enmascarado
        assert "[DOCUMENTO_ENMASCARADO]" in enmascarado
        assert "2026" in enmascarado  # El año 2026 NO debe ser enmascarado

    def test_enmascarar_celular_colombiano(self):
        """Enmascara números de teléfono móvil de 10 dígitos."""
        texto = "Por favor llamar a mi nuevo celular 3001234567 urgente."
        enmascarado = enmascarar_datos_personales(texto)
        assert "3001234567" not in enmascarado
        assert "[CELULAR_ENMASCARADO]" in enmascarado

    def test_enmascarar_correo_electronico(self):
        """Enmascara correos electrónicos corporativos o personales."""
        texto = "Mi nuevo correo es andres.p@correo-ficticio.com para notificaciones."
        enmascarado = enmascarar_datos_personales(texto)
        assert "andres.p@correo-ficticio.com" not in enmascarado
        assert "[CORREO_ENMASCARADO]" in enmascarado

    def test_texto_sin_datos_sensibles(self):
        """Un texto normal no debe sufrir alteraciones indebidas."""
        texto = "Solicito vacaciones del 7 al 11 de diciembre de 2026."
        assert enmascarar_datos_personales(texto) == texto


# ==============================================================================
# 3. PRUEBAS DE REGLAS DE REVISIÓN HUMANA (MISIÓN 3)
# ==============================================================================
class TestReglasRevisionHumana:
    def test_regla_saldo_insuficiente(self):
        """Si los días hábiles pedidos superan el saldo de vacaciones, requiere revisión."""
        solicitud = {"id_solicitud": "S06", "id_empleado": "E008"}
        prediccion = {
            "categoria": "VACACIONES",
            "confianza": 0.95,
            "fecha_inicio": "2026-12-21",
            "fecha_fin": "2026-12-31"
        }
        empleado_info = {
            "id_empleado": "E008",
            "nombre": "Felipe Castro",
            "dias_vacaciones_disponibles": 0
        }
        dias_habiles = 8  # Pide 8 teniendo 0
        
        saldo_suf, req_rev, motivo = evaluar_reglas_revision(
            solicitud, prediccion, empleado_info, dias_habiles
        )
        assert req_rev == "Sí"
        assert saldo_suf == "No"
        assert "exceden el saldo disponible" in motivo

    def test_regla_vacaciones_sin_fechas(self):
        """Vacaciones sin fechas definidas deben pasar inmediatamente a revisión."""
        solicitud = {"id_solicitud": "S09", "id_empleado": "E006"}
        prediccion = {
            "categoria": "VACACIONES",
            "confianza": 0.95,
            "fecha_inicio": None,
            "fecha_fin": None
        }
        empleado_info = {
            "id_empleado": "E006",
            "nombre": "Camilo Díaz",
            "dias_vacaciones_disponibles": 3
        }
        saldo_suf, req_rev, motivo = evaluar_reglas_revision(
            solicitud, prediccion, empleado_info, 0
        )
        assert req_rev == "Sí"
        assert "sin fechas de inicio y fin definidas" in motivo

    def test_regla_empleado_inexistente(self):
        """Solicitud de un empleado no registrado en nómina debe requerir revisión."""
        solicitud = {"id_solicitud": "S10", "id_empleado": "E009"}
        prediccion = {
            "categoria": "CERTIFICADO_LABORAL",
            "confianza": 0.98,
            "fecha_inicio": None,
            "fecha_fin": None
        }
        empleado_info = None  # No existe en la base de datos
        
        saldo_suf, req_rev, motivo = evaluar_reglas_revision(
            solicitud, prediccion, empleado_info, 0
        )
        assert req_rev == "Sí"
        assert "Empleado inexistente en la nómina" in motivo

    def test_regla_baja_confianza(self):
        """Si la confianza de la IA es menor a 0.80, debe requerir revisión humana."""
        solicitud = {"id_solicitud": "S08", "id_empleado": "E003"}
        prediccion = {
            "categoria": "OTRO",
            "confianza": 0.70,
            "fecha_inicio": None,
            "fecha_fin": None
        }
        empleado_info = {
            "id_empleado": "E003",
            "nombre": "María Torres",
            "dias_vacaciones_disponibles": 8
        }
        saldo_suf, req_rev, motivo = evaluar_reglas_revision(
            solicitud, prediccion, empleado_info, 0
        )
        assert req_rev == "Sí"
        assert "Baja confianza" in motivo

    def test_caso_valido_aprobacion_automatica(self):
        """Una solicitud válida con saldo suficiente no requiere revisión."""
        solicitud = {"id_solicitud": "S01", "id_empleado": "E001"}
        prediccion = {
            "categoria": "VACACIONES",
            "confianza": 0.96,
            "fecha_inicio": "2026-12-14",
            "fecha_fin": "2026-12-18"
        }
        empleado_info = {
            "id_empleado": "E001",
            "nombre": "Laura Gómez",
            "dias_vacaciones_disponibles": 12
        }
        dias_habiles = 5  # Pide 5 y tiene 12 disponibles
        
        saldo_suf, req_rev, motivo = evaluar_reglas_revision(
            solicitud, prediccion, empleado_info, dias_habiles
        )
        assert req_rev == "No"
        assert saldo_suf == "Sí"
        assert "Aprobación automática" in motivo


# ==============================================================================
# 4. PRUEBAS DE VALIDACIÓN DE RESPUESTAS JSON
# ==============================================================================
class TestValidacionJSON:
    def test_json_valido(self):
        payload = {
            "categoria": "VACACIONES",
            "confianza": 0.95,
            "fecha_inicio": "2026-12-14",
            "fecha_fin": "2026-12-18",
            "resumen": "Solicitud clara"
        }
        res = validar_json_ia(payload)
        assert res is not None
        assert res["categoria"] == "VACACIONES"
        assert res["confianza"] == 0.95

    def test_json_categoria_invalida(self):
        payload = {
            "categoria": "CATEGORIA_INVENTADA",
            "confianza": 0.95
        }
        assert validar_json_ia(payload) is None

