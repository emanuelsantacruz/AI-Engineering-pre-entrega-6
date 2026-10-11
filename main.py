import json
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from graph import build_graph

load_dotenv()


def main():
    app = build_graph()

    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = (
            "Tengo un presupuesto de $850.000 para armar una PC gamer. "
            "Recomiéndame procesador, placa de video, memoria RAM y fuente. "
            "Calcula si me alcanza el dinero y de cuántos Watts tiene que ser la fuente para que funcione bien."
        )

    print("Orquestador - Presupuesto PC Gaming")
    print(f"Consulta: \"{user_query}\"\n")

    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "current_task": None,
        "research_data": None,
        "analysis_data": None,
        "agent_history": [],
        "next_agent": "supervisor",
        "supervisor_reasoning": None,
        "validation_passed": False,
        "validation_feedback": None,
        "final_synthesis": None,
        "iteration_count": 0,
        "max_iterations": 5
    }

    config = {"recursion_limit": 15}
    trace = []
    final_state = None

    for output in app.stream(initial_state, config=config):
        for node_name, node_state in output.items():
            final_state = node_state
            print(f"Nodo: {node_name}")

            if node_name == "supervisor":
                print(f"  Decisión: {node_state.get('next_agent')}")
                print(f"  Motivo: {node_state.get('supervisor_reasoning')}")
            elif node_name == "researcher":
                print("  Componentes seleccionados por el investigador.")
            elif node_name == "analyst":
                print("  Cálculos de costos y fuente completados.")
            elif node_name == "validator":
                print(f"  Validación del presupuesto: {node_state.get('validation_passed')}")

            trace.append({
                "nodo": node_name,
                "iteracion": node_state.get("iteration_count"),
                "next_agent": node_state.get("next_agent"),
                "motivo": node_state.get("supervisor_reasoning")
            })

    print("\nPresupuesto Final:")
    if final_state and final_state.get("final_synthesis"):
        print(final_state["final_synthesis"])

    print("\nHistorial de agentes:")
    if final_state and final_state.get("agent_history"):
        for item in final_state["agent_history"]:
            print(f"- {item['agent']}: {item['summary']}")

    with open("trace_execution.json", "w", encoding="utf-8") as f:
        json.dump({
            "query": user_query,
            "trace": trace,
            "final_synthesis": final_state.get("final_synthesis") if final_state else ""
        }, f, indent=2, ensure_ascii=False)

    print("\nTraza guardada en trace_execution.json.")


if __name__ == "__main__":
    main()
