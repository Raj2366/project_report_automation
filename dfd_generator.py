import requests
from graphviz import Digraph
import os

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyCmFMR-XyUb2GdR1Hdub5_g_C6xjnpTqaA"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

def generate_dfd_text(topic):
    """Generate a textual description of a Data Flow Diagram (DFD) using the Gemini API."""
    data = {
        "contents": [{
            "parts": [{
                "text": f"Create a structured textual description of a Data Flow Diagram (DFD) for the topic: {topic}. Format it strictly as follows:\n\n"
                        "process: <process name>\n"
                        "data store: <data store name>\n"
                        "external entity: <external entity name>\n"
                        "data flow: <source> -> <destination>"
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

def generate_dfd_image(dfd_text, topic):
    """Generate a DFD image using Graphviz."""
    if not dfd_text:
        print("❌ No valid DFD text received.")
        return None

    try:
        # Parse the DFD text
        lines = dfd_text.split('\n')
        nodes = {}
        edges = []

        for line in lines:
            line = line.strip().lower()
            if line.startswith("process:"):
                process = line.split(":", 1)[1].strip().split(" (")[0]  # Remove parentheses
                nodes[process] = {"type": "process", "shape": "ellipse"}
            elif line.startswith("data store:"):
                data_store = line.split(":", 1)[1].strip().split(" (")[0]  # Remove parentheses
                nodes[data_store] = {"type": "data_store", "shape": "rectangle"}
            elif line.startswith("external entity:"):
                entity = line.split(":", 1)[1].strip().split(" (")[0]  # Remove parentheses
                nodes[entity] = {"type": "external_entity", "shape": "rectangle"}
            elif line.startswith("data flow:"):
                parts = [part.strip().split(" (")[0] for part in line.split(":", 1)[1].split("->")]  # Remove parentheses
                if len(parts) == 2:
                    source, destination = parts
                    if source and destination:
                        edges.append((source, destination))

        # Create a Graphviz Digraph
        dot = Digraph(comment="Data Flow Diagram", format="png")
        dot.attr(rankdir="LR")  # Left-to-right layout
        dot.attr(size="24,18")  # Increase image size (24 inches x 18 inches)
        dot.attr(ratio="fill")  # Stretch the image to fill the specified size
        dot.attr(dpi="300")  # Increase DPI for better resolution

        # Add nodes
        for node, node_info in nodes.items():
            if node_info["shape"] == "ellipse":
                dot.node(node, shape="ellipse", style="filled", fillcolor="lightblue", fontsize="60", width="3.5", height="3", label=node)  # Increased font size and node size
            elif node_info["shape"] == "rectangle":
                if node_info["type"] == "data_store":
                    dot.node(node, shape="rectangle", style="filled", fillcolor="lightgreen", fontsize="60", width="3.5", height="3", label=node)  # Increased font size and node size
                else:
                    dot.node(node, shape="rectangle", style="filled", fillcolor="lightcoral", fontsize="60", width="3.5", height="3", label=node)  # Increased font size and node size

        # Add edges
        for (source, destination) in edges:
            dot.edge(source, destination, len="1", color="#333333", penwidth="2.5", arrowsize="1.2")  # Increase edge length

        # Save the image
        output_folder = "generated_diagrams"
        os.makedirs(output_folder, exist_ok=True)
        image_path = os.path.join(output_folder, f"{topic}_dfd")
        dot.render(image_path, cleanup=True)

        print(f"🟢 DFD image saved at: {image_path}.png")
        return f"{image_path}.png"

    except Exception as e:
        print(f"❌ Error generating DFD image: {e}")
        return None

