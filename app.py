from flask import Flask, render_template, request, send_file, jsonify
import os
import requests
import logging
import tempfile
import shutil
import uuid
import mimetypes
import json
from werkzeug.utils import secure_filename
from docx2pdf import convert
from main_page import create_project_file, save_uploaded_files, process_images
from image_generate import generate_image
from datetime import datetime
import pythoncom

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = "temp_uploads"
app.config['GENERATED_IMAGES'] = "static/generated"
app.config['LOGO_IMAGES'] = "static/logo_images"
app.config['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', 'AIzaSyABI3AMv_sZb5ZC3CjNZcwHS9UewbNmQ40')
app.config['GOOGLE_CSE_ID'] = os.getenv('GOOGLE_CSE_ID', '742b69a79adbf406d')

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler('app.log'),
                        logging.StreamHandler()
                    ])

# Ensure all required directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_IMAGES'], exist_ok=True)
os.makedirs(app.config['LOGO_IMAGES'], exist_ok=True)
os.makedirs('generated_docs/project_reports', exist_ok=True)
os.makedirs('generated_docs/project_synopsis', exist_ok=True)
os.makedirs('generated_docs/temp_pdf', exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def get_image_extension(content_type):
    """Get file extension from content type"""
    return mimetypes.guess_extension(content_type)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_custom_sections(custom_sections_str):
    """
    Parse custom sections string into individual sections, handling commas within section titles.
    Uses a simple heuristic: if a comma is followed by a space, it's a separator.
    Otherwise, it's part of the section title.
    """
    sections = []
    current_section = []
    
    for part in custom_sections_str.split(','):
        part = part.strip()
        if not part:
            continue
            
        # If the part starts with a capital letter (after any leading spaces)
        # and we have content in current_section, consider it a new section
        if current_section and part and part[0].isupper():
            sections.append(', '.join(current_section))
            current_section = [part]
        else:
            current_section.append(part)
    
    if current_section:
        sections.append(', '.join(current_section))
    
    return sections

def download_and_save_logos(logo_urls_json):
    """Download and save multiple logos to app.config['LOGO_IMAGES']"""
    saved_logos = []
    try:
        logo_data = json.loads(logo_urls_json)
        for logo in logo_data:
            try:
                response = requests.get(logo['url'], stream=True, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "").lower()
                    ext = get_image_extension(content_type) or '.jpg'
                    logo_filename = f"{uuid.uuid4().hex}{ext}"
                    logo_path = os.path.join(app.config['LOGO_IMAGES'], logo_filename)

                    os.makedirs(app.config['LOGO_IMAGES'], exist_ok=True)

                    with open(logo_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)

                    saved_logos.append(logo_path)
            except Exception as e:
                logging.error(f"Error downloading logo {logo.get('url', '')}: {e}")
                continue
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing logo URLs JSON: {e}")

    return saved_logos

def generate_unique_filename(base_name):
    """Generate a unique filename with timestamp and random string"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = uuid.uuid4().hex[:6]
    safe_name = "".join([c if c.isalnum() else "_" for c in base_name])
    return f"{safe_name[:50]}_{timestamp}_{random_str}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        report_type = request.form.get("report_type", "college")
        form_data = {
            'topic': request.form.get("topic", "").strip(),
            'submitted_by': request.form.get("submitted_by", "").strip(),
            'submitted_to': request.form.get("submitted_to", "").strip(),
            'course_name': request.form.get("course_name", "").strip(),
            'semester_name': request.form.get("semester_name", "").strip(),
            'designate': request.form.get("designate", "").strip(),
            'institute_name': request.form.get("institute_name", "").strip(),
            'location': request.form.get("location", "").strip(),
            'department': request.form.get("department", "").strip(),
            'enrollment': request.form.get("enrollment", "").strip(),
            'selected_sections': request.form.getlist("selected_sections"),
            'custom_sections': request.form.get("custom_sections", "").strip(),
            'ordered_sections': request.form.get("ordered_sections", "").strip(),
            'college_logo_urls': request.form.get("college_logo_urls", "").strip(),
            'school_logo_urls': request.form.get("school_logo_urls", "").strip(),
            'active_report_type': report_type
        }

        try:
            if not all([form_data['topic'], form_data['submitted_by'], form_data['submitted_to']]):
                raise ValueError("Please fill all required fields!")

            custom_sections = [s.strip() for s in form_data['custom_sections'].split(",") if s.strip()]
            ordered_sections = [s.strip() for s in form_data['ordered_sections'].split(",") if s.strip()]

            temp_dir = tempfile.mkdtemp(dir=app.config['UPLOAD_FOLDER'])

            try:
                project_images = []
                if 'project_images' in request.files:
                    project_files = request.files.getlist('project_images')
                    project_images = save_uploaded_files(
                        [f for f in project_files if f and allowed_file(f.filename)],
                        temp_dir
                    )

                code_images = []
                if report_type == 'college' and 'code_screenshots' in request.files:
                    code_files = request.files.getlist('code_screenshots')
                    code_images = save_uploaded_files(
                        [f for f in code_files if f and allowed_file(f.filename)],
                        temp_dir
                    )

                if 'selected_project_images' in request.form:
                    generated_images = request.form['selected_project_images'].split(',')
                    for img_name in generated_images:
                        if img_name:
                            img_path = os.path.join(app.config['GENERATED_IMAGES'], img_name)
                            if os.path.exists(img_path):
                                project_images.append(img_path)

                logo_urls_json = form_data['college_logo_urls'] if report_type == 'college' else form_data['school_logo_urls']
                logo_paths = download_and_save_logos(logo_urls_json) if logo_urls_json else []

                kwargs = {
                    'topic': form_data['topic'],
                    'submitted_by': form_data['submitted_by'],
                    'submitted_to': form_data['submitted_to'],
                    'course_name': form_data['course_name'],
                    'semester_name': form_data['semester_name'],
                    'designate': form_data['designate'],
                    'institute_name': form_data['institute_name'],
                    'location': form_data['location'],
                    'department': form_data['department'],
                    'enrollment': form_data['enrollment'],
                    'selected_sections': form_data['selected_sections'],
                    'custom_sections': custom_sections,
                    'ordered_sections': ordered_sections,
                    'project_images': project_images,
                    'code_images': code_images if report_type == 'college' else None,
                    'report_type': report_type,
                    'logo_paths': logo_paths
                }

                # if report_type == 'college':
                #     kwargs['location'] = form_data['location']

                base_filename = generate_unique_filename(form_data['topic'])
                filename = create_project_file(base_filename=base_filename, **kwargs)

                return render_template("index.html",
                                   success=True,
                                   filename=filename,
                                   report_type=report_type,
                                   **form_data)

            finally:
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logging.warning(f"Could not clean up temp directory {temp_dir}: {e}")

        except Exception as e:
            logging.error(f"Error in form processing: {e}", exc_info=True)
            return render_template("index.html",
                               error=str(e),
                               report_type=report_type,
                               **form_data)

    return render_template("index.html", report_type="college", active_report_type="college")

@app.route("/search-logo")
def search_logo():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        api_key = app.config['GOOGLE_API_KEY']
        cx = app.config['GOOGLE_CSE_ID']

        if not api_key or not cx:
            return jsonify({'error': 'Search API not configured'}), 500

        url = f"https://www.googleapis.com/customsearch/v1?q={query}&searchType=image&key={api_key}&cx={cx}&num=6"
        response = requests.get(url)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        logging.error(f"Error in logo search: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/generate-image", methods=["POST"])
def generate_image_route():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    report_type = data.get('report_type', 'college')

    if not prompt:
        return jsonify({'error': 'Prompt cannot be empty'}), 400

    image_path = generate_image(prompt, report_type)

    if image_path:
        rel_path = os.path.join('static', 'generated', os.path.basename(image_path))
        return jsonify({
            'success': True,
            'imageUrl': rel_path,
            'imageName': os.path.basename(image_path),
            'message': 'Image generated successfully'
        })
    else:
        return jsonify({
            'error': 'Image generation failed. Please try a different prompt.',
            'success': False
        }), 500

@app.route("/download/<filename>")
def download_file(filename):
    try:
        format_type = request.args.get('format', 'docx')
        base_filename = os.path.splitext(filename)[0]
        
        if format_type == 'docx':
            # Existing Word document download logic
            docx_path = None
            for subdir in ['project_reports', 'project_synopsis']:
                test_path = os.path.join('generated_docs', subdir, f"{base_filename}.docx")
                if os.path.exists(test_path):
                    docx_path = test_path
                    break
            else:
                raise FileNotFoundError(f"Word file {base_filename}.docx not found")

            return send_file(
                docx_path,
                as_attachment=True,
                download_name=f"{base_filename}.docx",
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        
        elif format_type == 'pdf':
            # Find the source Word document
            docx_path = None
            for subdir in ['project_reports', 'project_synopsis']:
                test_path = os.path.join('generated_docs', subdir, f"{base_filename}.docx")
                if os.path.exists(test_path):
                    docx_path = test_path
                    break
            else:
                raise FileNotFoundError(f"Word file {base_filename}.docx not found")

            # Generate completely fresh PDF with unique name
            temp_pdf_dir = os.path.join('generated_docs', 'temp_pdf')
            os.makedirs(temp_pdf_dir, exist_ok=True)
            
            # Create unique PDF filename
            unique_id = uuid.uuid4().hex[:8]
            temp_pdf_name = f"{base_filename}_{unique_id}.pdf"
            temp_pdf_path = os.path.join(temp_pdf_dir, temp_pdf_name)
            
            try:
                # Initialize COM for Windows
                pythoncom.CoInitialize()
                
                # Convert to PDF
                convert(docx_path, temp_pdf_path)
                
                # Create response with cleanup handler
                response = send_file(
                    temp_pdf_path,
                    as_attachment=True,
                    download_name=f"{base_filename}.pdf",  # Nice filename for user
                    mimetype='application/pdf'
                )
                
                # Clean up the temp file after download completes
                @response.call_on_close
                def cleanup_temp_pdf():
                    try:
                        pythoncom.CoUninitialize()
                        if os.path.exists(temp_pdf_path):
                            os.remove(temp_pdf_path)
                            logging.info(f"Cleaned up temp PDF: {temp_pdf_path}")
                    except Exception as e:
                        logging.error(f"Error cleaning temp PDF {temp_pdf_path}: {e}")
                
                return response
                
            except Exception as e:
                # Clean up if conversion fails
                pythoncom.CoUninitialize()
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                logging.error(f"PDF conversion failed: {e}")
                raise Exception("PDF conversion failed. Please try downloading the Word version.")

        else:
            raise ValueError("Invalid format specified")
            
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return render_template("index.html", error=f"Download failed: {str(e)}"), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)