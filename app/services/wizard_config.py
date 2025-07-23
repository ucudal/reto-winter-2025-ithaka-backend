from typing import Dict, List
from app.schemas.chat_schemas import WizardStep

# Configuración de las 20 preguntas del wizard de postulación
WIZARD_STEPS: List[WizardStep] = [
    # Datos Personales (Preguntas 1-12)
    WizardStep(
        step_number=1,
        question="¡Hola! Soy tu asistente para la postulación a Ithaka. ¿Podrías decirme tu apellido y nombre completo?",
        field_name="full_name",
        validation_type="text",
        required=True
    ),
    WizardStep(
        step_number=2,
        question="Perfecto. Ahora necesito tu correo electrónico para poder contactarte.",
        field_name="email",
        validation_type="email",
        required=True
    ),
    WizardStep(
        step_number=3,
        question="¿Cuál es tu número de celular o teléfono?",
        field_name="phone",
        validation_type="phone",
        required=True
    ),
    WizardStep(
        step_number=4,
        question="¿Podrías proporcionarme tu número de documento de identidad?",
        field_name="document_id",
        validation_type="text",
        required=True
    ),
    WizardStep(
        step_number=5,
        question="¿En qué país y localidad resides actualmente?",
        field_name="country_city",
        validation_type="text",
        required=True
    ),
    WizardStep(
        step_number=6,
        question="¿En qué Campus de la UCU preferís contactarte con Ithaka?",
        field_name="campus_preference",
        validation_type="select",
        options=["Maldonado", "Montevideo", "Salto"],
        required=True
    ),
    WizardStep(
        step_number=7,
        question="¿Cuál es tu relación con la UCU?",
        field_name="ucu_relation",
        validation_type="select",
        options=["Estudiante", "Graduado", "Funcionario o Docente",
                 "Solía estudiar allí", "No tengo relación"],
        required=True
    ),
    WizardStep(
        step_number=8,
        question="En caso de tener relación con la UCU, ¿en qué facultad estudiaste/trabajas?",
        field_name="faculty",
        validation_type="select",
        options=["Ciencias de la Salud", "Ciencias Empresariales",
                 "Ciencias Humanas + Derecho", "Ingeniería y Tecnologías", "No aplica"],
        required=False,
        depends_on={"ucu_relation": [
            "Estudiante", "Graduado", "Funcionario o Docente", "Solía estudiar allí"]}
    ),
    WizardStep(
        step_number=9,
        question="¿Cómo llegaste a Ithaka?",
        field_name="how_found_ithaka",
        validation_type="select",
        options=[
            "Redes Sociales",
            "Curso de Grado",
            "Curso de Posgrado",
            "Buscando en la web",
            "Por alguna actividad de UCU",
            "A través de ANII/ANDE cuando buscaba una IPE"
        ],
        required=True
    ),
    WizardStep(
        step_number=10,
        question="¿Qué te motiva para escribirnos? Me encantaría conocer tu historia.",
        field_name="motivation",
        validation_type="text",
        required=True
    ),
    WizardStep(
        step_number=11,
        question="¿Tienes una idea o emprendimiento?",
        field_name="has_idea",
        validation_type="boolean",
        options=["Sí", "No"],
        required=True
    ),
    WizardStep(
        step_number=12,
        question="¡Muchas gracias por compartir tus datos! ¿Hay comentarios adicionales que quieras agregar?",
        field_name="additional_comments",
        validation_type="text",
        required=False
    ),

    # Preguntas adicionales solo para quienes tienen idea/emprendimiento (Preguntas 13-20)
    WizardStep(
        step_number=13,
        question="¡Excelente que tengas una idea! Si tienes equipo de trabajo, ¿cómo está compuesto? Por favor compárteme los datos de los otros integrantes (nombres, celulares, correos) y qué actividades/roles desempeña cada uno.",
        field_name="team_members_data",
        validation_type="text",
        required=False,
        depends_on={"has_idea": True}
    ),
    WizardStep(
        step_number=14,
        question="¿Es tu primer emprendimiento? Cuéntame sobre tus experiencias previas.",
        field_name="is_first_venture",
        validation_type="boolean_with_text",
        required=True,
        depends_on={"has_idea": True}
    ),
    WizardStep(
        step_number=15,
        question="¿Qué problema resuelve tu emprendimiento? ¿Qué oportunidad o necesidad has detectado?",
        field_name="problem_opportunity",
        validation_type="text",
        required=True,
        depends_on={"has_idea": True}
    ),
    WizardStep(
        step_number=16,
        question="¿Cuál es la solución que propones? ¿Quiénes son tus clientes objetivo?",
        field_name="solution_clients",
        validation_type="text",
        required=True,
        depends_on={"has_idea": True}
    ),
    WizardStep(
        step_number=17,
        question="¿Por qué tu emprendimiento es innovador o tiene valor diferencial? Explícame también: ¿Cómo se resuelve este problema hoy? ¿Por qué te van a comprar a ti en vez de a otros?",
        field_name="innovation_differential",
        validation_type="text",
        required=True,
        depends_on={"has_idea": True}
    ),
    WizardStep(
        step_number=18,
        question="¿Cómo hace dinero este proyecto? Cuéntame sobre tu modelo de negocio.",
        field_name="business_model",
        validation_type="text",
        required=True,
        depends_on={"has_idea": True}
    ),
    WizardStep(
        step_number=19,
        question="¿En qué etapa está tu proyecto actualmente?",
        field_name="project_stage",
        validation_type="select",
        options=[
            "Solo tengo la idea",
            "Estoy validando la idea",
            "Tengo un prototipo",
            "Ya tengo algunos clientes",
            "Estoy escalando el negocio"
        ],
        required=True,
        depends_on={"has_idea": True}
    ),
    WizardStep(
        step_number=20,
        question="¿Cuál de estos apoyos necesitas de Ithaka?",
        field_name="support_needed",
        validation_type="multiple_select",
        options=[
            "Tutoría para validar la idea",
            "Soporte para armar el plan de negocios",
            "Ayuda para obtener financiamiento para el proyecto",
            "Capacitación",
            "Ayuda para un tema específico",
            "Otro"
        ],
        required=True,
        depends_on={"has_idea": True}
    ),
    WizardStep(
        step_number=21,
        question="¿Algo más que quieras contarnos sobre tu proyecto?",
        field_name="additional_info",
        validation_type="text",
        required=False,
        depends_on={"has_idea": True}
    )
]

# Mapeo de campos a pasos para fácil acceso
FIELD_TO_STEP: Dict[str, int] = {
    step.field_name: step.step_number for step in WIZARD_STEPS}

# Función para obtener el siguiente paso basado en las respuestas actuales


def get_next_step(current_step: int, application_data: Dict) -> int:
    """
    Determina el siguiente paso basado en el paso actual y los datos de la aplicación
    """
    # Si no tiene idea, saltar preguntas 13-21
    if current_step == 11 and not application_data.get("has_idea"):
        return 12  # Ir directamente a comentarios adicionales y terminar

    # Si terminó las preguntas básicas y no tiene idea
    if current_step == 12 and not application_data.get("has_idea"):
        return -1  # Terminar wizard

    # Lógica normal: siguiente paso
    next_step = current_step + 1

    # Verificar si el siguiente paso existe y cumple dependencias
    if next_step <= len(WIZARD_STEPS):
        step = WIZARD_STEPS[next_step - 1]  # -1 porque la lista es 0-indexed

        # Verificar dependencias
        if step.depends_on:
            for field, required_values in step.depends_on.items():
                if isinstance(required_values, bool):
                    if application_data.get(field) != required_values:
                        return get_next_step(next_step, application_data)
                elif isinstance(required_values, list):
                    if application_data.get(field) not in required_values:
                        return get_next_step(next_step, application_data)

        return next_step

    return -1  # Fin del wizard


def get_step_by_number(step_number: int) -> WizardStep:
    """
    Obtiene un paso específico por su número
    """
    for step in WIZARD_STEPS:
        if step.step_number == step_number:
            return step
    raise ValueError(f"Paso {step_number} no encontrado")


def is_wizard_complete(application_data: Dict) -> bool:
    """
    Verifica si el wizard está completo basado en los datos actuales
    """
    required_basic_fields = ["full_name", "email", "phone", "document_id", "country_city",
                             "campus_preference", "ucu_relation", "how_found_ithaka", "motivation", "has_idea"]

    # Verificar campos básicos
    for field in required_basic_fields:
        if not application_data.get(field):
            return False

    # Si tiene idea, verificar campos adicionales requeridos
    if application_data.get("has_idea"):
        required_idea_fields = ["problem_opportunity", "solution_clients", "innovation_differential",
                                "business_model", "project_stage", "support_needed"]
        for field in required_idea_fields:
            if not application_data.get(field):
                return False

    return True
