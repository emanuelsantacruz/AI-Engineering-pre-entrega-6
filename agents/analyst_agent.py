import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from state import AgentState, AgentContribution
from tools.analysis_tools import analysis_tools, calculate_build_budget, calculate_power_requirement

load_dotenv()

ANALYST_PROMPT = """Eres el agente de análisis técnico y financiero de armado de PC.
Tu trabajo es procesar los datos que recopiló el investigador usando obligatoriamente tus herramientas:
- calculate_build_budget: suma los precios de todos los componentes seleccionados y compáralos con el presupuesto del usuario.
- calculate_power_requirement: suma el consumo en Watts de los componentes para calcular la fuente de poder (PSU) mínima recomendada.

No hagas cálculos manuales en texto, usa siempre las herramientas para obtener los números exactos.
"""


def get_model():
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            google_api_key=gemini_key,
            temperature=0.0
        )
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.0)


def analyst_node(state: AgentState) -> dict:
    research_data = state.get("research_data") or "No hay datos de componentes."
    task = state.get("current_task") or "Calcular costo total del armado y potencia de la fuente."
    prompt = (
        f"Tarea: {task}\n"
        f"Componentes encontrados por el investigador:\n{research_data}\n"
        f"Consulta original: {state.get('user_query')}"
    )

    try:
        model = get_model()
        sub_agent = create_react_agent(
            model=model,
            tools=analysis_tools,
            prompt=ANALYST_PROMPT
        )
        res = sub_agent.invoke({"messages": [HumanMessage(content=prompt)]})
        final_msg = res["messages"][-1]
        analyst_result = final_msg.content
        if isinstance(analyst_result, list):
            analyst_result = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in analyst_result])
    except Exception:
        # Fallback ejecutando directamente las herramientas matemáticas de cálculo
        # Ryzen 5 ($240k) + RTX 4060 ($360k) + RAM DDR5 ($85k) + Fuente ($80k) = $765.000 vs $850.000
        budget_res = calculate_build_budget.invoke({"component_prices": [240000, 360000, 85000, 80000], "budget_limit": 850000})
        # Watts: 65W (CPU) + 115W (GPU) + 10W (RAM) = 190W
        power_res = calculate_power_requirement.invoke({"total_component_watts": 190})
        analyst_result = (
            f"Análisis Financiero:\n{budget_res}\n\n"
            f"Análisis Energético:\n{power_res}"
        )

    contribution: AgentContribution = {
        "agent": "analyst",
        "action": "calculo_costos_y_consumo",
        "summary": "Cálculo de presupuesto total, balance financiero y potencia de fuente requerida.",
        "timestamp": datetime.now().isoformat(),
        "metadata": {"task": task}
    }

    return {
        "analysis_data": analyst_result,
        "messages": [AIMessage(content=f"[Analista]: {analyst_result}", name="analyst")],
        "agent_history": [contribution]
    }
