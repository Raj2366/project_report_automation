import requests
from graphviz import Digraph
import os

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyCmFMR-XyUb2GdR1Hdub5_g_C6xjnpTqaA"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

def generate_flowchart_text(topic):
    """Generate a textual description of a Flowchart for the given topic using the Gemini API."""
    data = {
        "contents": [{
            "parts": [{
                "text": f"Create a structured textual description of a Flowchart for the topic: {topic}. Format it strictly as follows:\n\n"
                        "process: <process name>\n"
                        "decision: <decision name>\n"
                        "start/end: <start/end name>\n"
                        "flow: <source> -> <destination>"
            }]
        }]
    }

    params = {'key': GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_URL, headers=HEADERS, params=params, json=data)
        response.raise_for_status()
        content = response.json()
        
        # Ensure correct parsing of the response
        if 'candidates' in content and content['candidates']:
            text_response = content['candidates'][0]['content']['parts'][0].get('text', '')
            return text_response.strip() if text_response else None
        
        return None  # If no valid response
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return None

def generate_flowchart_image(flowchart_text, topic):
    """Generate a Flowchart image using Graphviz."""
    if not flowchart_text:
        print("❌ No valid Flowchart text received.")
        return None

    try:
        # Parse the Flowchart text
        lines = flowchart_text.split('\n')
        nodes = {}
        edges = []

        # start_node = "Start"
        # end_node = "End"
        # nodes[start_node] = {"type": "start_end", "shape": "ellipse"}
        # nodes[end_node] = {"type": "start_end", "shape": "ellipse"}

        for line in lines:
            line = line.strip().lower()
            if line.startswith("process:"):
                process = line.split(":", 1)[1].strip().split(" (")[0]  # Remove parentheses
                nodes[process] = {"type": "process", "shape": "rectangle"}
            elif line.startswith("decision:"):
                decision = line.split(":", 1)[1].strip().split(" (")[0]  # Remove parentheses
                nodes[decision] = {"type": "decision", "shape": "diamond"}
            elif line.startswith("start/end:"):
                start_end = line.split(":", 1)[1].strip().split(" (")[0]  # Remove parentheses
                nodes[start_end] = {"type": "start_end", "shape": "ellipse"}
            elif line.startswith("flow:"):
                parts = [part.strip().split(" (")[0] for part in line.split(":", 1)[1].split("->")]  # Remove parentheses
                if len(parts) == 2:
                    source, destination = parts
                    if source and destination:
                        edges.append((source, destination))

        # Create a Graphviz Digraph
        dot = Digraph(comment="Flowchart", format="png")
        dot.attr(rankdir="TB")  # Top-to-bottom layout
        dot.attr(size="12,15")  # Adjusted size (12 inches x 18 inches)
        dot.attr(ratio="fill")  # Stretch the image to fill the specified size
        dot.attr(dpi="300")  # Increase DPI for better resolution

        # Add nodes
        for node, node_info in nodes.items():
            if node_info["type"] == "start_end":
                dot.node(node, shape="ellipse", style="filled", fillcolor="orange", fontsize="20", width="2.5", height="1", label=node)  # Start/End node
            elif node_info["type"] == "process":
                dot.node(node, shape="rectangle", style="filled", fillcolor="yellow", fontsize="20", width="2.5", height="1", label=node)  # Process node
            elif node_info["type"] == "decision":
                dot.node(node, shape="diamond", style="filled", fillcolor="violet", fontsize="20", width="2.5", height="1", label=node)  # Decision node

        # Add edges with fixed length, darker color, increased width, and wider arrow points
        for (source, destination) in edges:
            dot.edge(
                source, 
                destination, 
                len="1",  # Fixed edge length (1.5 inches)
                color="#333333",  # Darker color (#333333)
                penwidth="1.5",  # Increased edge width (2.0)
                arrowsize="1.2"  # Wider arrow points (1.2)
            )

        # Save the image
        output_folder = "generated_flowcharts"
        os.makedirs(output_folder, exist_ok=True)
        image_path = os.path.join(output_folder, f"{topic}_flowchart")
        dot.render(image_path, cleanup=True)

        print(f"🟢 Flowchart image saved at: {image_path}.png")
        return f"{image_path}.png"

    except Exception as e:
        print(f"❌ Error generating Flowchart image: {e}")
        return None