import os
import secrets
import logging
import tempfile
import magic
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from crypto_utils import (
    hash_file, 
    generate_key_pair, 
    save_keys, 
    load_public_key, 
    load_private_key,
    sign_file,
    verify_signature,
    save_signature,
    load_signature
)
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, abort, Response, jsonify

# Configuration
app = Flask(__name__, template_folder='templates')
app.secret_key = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'pem', 'sig'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Create challenges directory if it doesn't exist
challenges_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'challenges')
os.makedirs(challenges_dir, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def is_file_allowed(file_stream):
    """Check file content using magic numbers"""
    try:
        file_stream.seek(0)
        mime = magic.from_buffer(file_stream.read(2048), mime=True)
        file_stream.seek(0)
        return mime in {
            'text/plain', 'application/pdf', 
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg', 'image/png', 'application/octet-stream'
        }
    except Exception as e:
        logger.error(f"File validation error: {str(e)}")
        return False

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/keys')
def keys_page():
    """Display generated keys page"""
    if 'private_key' not in session or 'public_key' not in session:
        flash('No keys found! Please generate keys first.', 'error')
        return redirect(url_for('generate_keys_route'))
    return render_template('keys.html')


@app.route('/generate_keys', methods=['POST'])
def generate_keys_route():
    try:
        private_key, public_key = generate_key_pair()
        session['private_key'] = private_key
        session['public_key'] = public_key
        flash('Keys generated successfully.', 'success')
        return redirect(url_for('keys_page'))
    except Exception as e:
        logger.error(f"Key generation error: {str(e)}")
        flash('Error generating keys.', 'error')
        return redirect(url_for('index'))
@app.route('/generate_keys', methods=['GET'])
def generate_keys_route_get():
    """Render the key generation page"""
    return render_template('generate_keys.html')

@app.route('/run_tests')
def run_tests():
    import subprocess
    result = subprocess.run(['python3', 'test_signature.py'], capture_output=True, text=True)
    return f"<pre>{result.stdout or result.stderr}</pre>"


        



@app.route('/download_key/<key_type>')
def download_key(key_type):
    """Download a generated key"""
    if key_type not in ['private', 'public']:
        flash('Invalid key type!', 'error')
        return redirect(url_for('generate_keys_route'))
    
    if key_type + '_key' not in session:
        flash('No keys found! Please generate keys first.', 'error')
        return redirect(url_for('generate_keys_route'))
    
    key_content = session[key_type + '_key']
    filename = key_type + '.pem'
    
    response = Response(
        key_content,
        mimetype='application/x-pem-file',
        headers={'Content-Disposition': f'attachment;filename={filename}'}
    )
    
    return response
    """Download a generated key"""
    if key_type not in ['private', 'public']:
        flash('Invalid key type!', 'error')
        return redirect(url_for('generate_keys_route'))
    
    if key_type + '_key' not in session:
        flash('No keys found! Please generate keys first.', 'error')
        return redirect(url_for('generate_keys_route'))
    
    key_content = session[key_type + '_key']
    filename = key_type + '.pem'
    
    response = Response(
        key_content,
        mimetype='application/x-pem-file',
        headers={'Content-Disposition': f'attachment;filename={filename}'}
    )
    
    return response

@app.route('/sign_document', methods=['GET', 'POST'])
def sign_document():
    """Sign a document using a private key"""
    if request.method == 'POST':
        try:
            if 'document' not in request.files or 'private_key' not in request.files:
                flash('Missing document or private key!', 'error')
                return redirect(request.url)
            
            document = request.files['document']
            private_key_file = request.files['private_key']
            
            if document.filename == '' or private_key_file.filename == '':
                flash('No selected file!', 'error')
                return redirect(request.url)
            
            if not (document and allowed_file(document.filename) and private_key_file):
                flash('Invalid file type!', 'error')
                return redirect(request.url)
            
            # Validate file contents
            if not is_file_allowed(document.stream) or not is_file_allowed(private_key_file.stream):
                flash('Invalid file content detected!', 'error')
                return redirect(request.url)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save files with secure names
                document_filename = secure_filename(document.filename)
                document_path = os.path.join(temp_dir, document_filename)
                document.save(document_path)
                
                private_key_path = os.path.join(temp_dir, 'private.pem')
                private_key_file.save(private_key_path)
                
                # Sign the document
                signature = sign_file(document_path, private_key_path)
                
                # Save the signature
                signature_filename = document_filename + '.sig'
                signature_path = os.path.join(temp_dir, signature_filename)
                save_signature(signature, signature_path)
                
                # Store in session for download
                session['signature_filename'] = signature_filename
                session['document_name'] = document_filename
                
                # Save signature to uploads for temporary access
                final_signature_path = os.path.join(app.config['UPLOAD_FOLDER'], signature_filename)
                save_signature(signature, final_signature_path)
                
                return redirect(url_for('signature_result'))
        except Exception as e:
            logger.error(f"Signing error: {str(e)}")
            flash(f'Error signing document: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('sign_document.html')

@app.route('/signature_result')
def signature_result():
    """Show signature result page"""
    if 'signature_filename' not in session or 'document_name' not in session:
        flash('No signature found!', 'error')
        return redirect(url_for('sign_document'))
    
    return render_template('signature_result.html', 
                         document_name=session['document_name'],
                         signature_name=session['signature_filename'])

@app.route('/download_signature')
def download_signature():
    """Download the generated signature"""
    if 'signature_filename' not in session:
        flash('No signature found!', 'error')
        return redirect(url_for('sign_document'))
    
    signature_filename = session['signature_filename']
    signature_path = os.path.join(app.config['UPLOAD_FOLDER'], signature_filename)
    
    if not os.path.exists(signature_path):
        flash('Signature file not found!', 'error')
        return redirect(url_for('sign_document'))
    
    return send_file(signature_path, 
                    mimetype='application/octet-stream',
                    as_attachment=True,
                    download_name=signature_filename)

@app.route('/verify_signature', methods=['GET', 'POST'])
def verify_signature_route():
    """Verify a document signature using a public key"""
    if request.method == 'POST':
        try:
            if not all(field in request.files for field in ['document', 'signature', 'public_key']):
                flash('Missing required files!', 'error')
                return redirect(request.url)
            
            document = request.files['document']
            signature_file = request.files['signature']
            public_key_file = request.files['public_key']
            
            if any(f.filename == '' for f in [document, signature_file, public_key_file]):
                flash('One or more files not selected!', 'error')
                return redirect(request.url)
            
            # Validate file extensions
            if not (allowed_file(document.filename) and 
                   allowed_file(signature_file.filename) and 
                   allowed_file(public_key_file.filename)):
                flash('Invalid file type!', 'error')
                return redirect(request.url)
            
            # Validate file contents
            if not (is_file_allowed(document.stream) and 
                   is_file_allowed(public_key_file.stream)):
                flash('Invalid file content detected!', 'error')
                return redirect(request.url)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save files with secure names
                doc_path = os.path.join(temp_dir, secure_filename(document.filename))
                sig_path = os.path.join(temp_dir, secure_filename(signature_file.filename))
                key_path = os.path.join(temp_dir, secure_filename(public_key_file.filename))
                
                document.save(doc_path)
                signature_file.save(sig_path)
                public_key_file.save(key_path)
                
                # Load and verify signature
                signature = load_signature(sig_path)
                is_valid = verify_signature(doc_path, signature, key_path)
                
                # Store results
                session['verification_result'] = is_valid
                session['document_name'] = document.filename
                
                return redirect(url_for('verification_result'))
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            flash(f'Verification failed: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('verify_signature.html')

@app.route('/verification_result')
def verification_result():
    """Display the verification result"""
    if 'verification_result' not in session or 'document_name' not in session:
        flash('No verification result found!', 'error')
        return redirect(url_for('verify_signature_route'))
    
    is_valid = session['verification_result']
    document_name = session['document_name']
    
    return render_template('verification_result.html', 
                         is_valid=is_valid,
                         document_name=document_name)

@app.route('/forensic_challenges')
def forensic_challenges():
    """Display available forensic challenges"""
    challenges_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'challenges')
    challenges = []
    
    if os.path.exists(challenges_dir):
        for challenge_dir in os.listdir(challenges_dir):
            challenge_path = os.path.join(challenges_dir, challenge_dir)
            if os.path.isdir(challenge_path):
                desc_path = os.path.join(challenge_path, 'description.txt')
                description = "No description available."
                if os.path.exists(desc_path):
                    with open(desc_path, 'r') as f:
                        description = f.read()
                
                files = []
                for filename in os.listdir(challenge_path):
                    if filename != 'description.txt' and os.path.isfile(os.path.join(challenge_path, filename)):
                        files.append(filename)
                
                challenges.append({
                    'id': challenge_dir,
                    'name': challenge_dir.replace('_', ' ').title(),
                    'description': description,
                    'files': files
                })
    
    return render_template('challenges.html', challenges=challenges)

@app.route('/challenge/<challenge_id>')
def challenge(challenge_id):
    """Display a specific forensic challenge"""
    challenge_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'challenges', challenge_id)
    
    if not os.path.exists(challenge_dir) or not os.path.isdir(challenge_dir):
        flash('Challenge not found!', 'error')
        return redirect(url_for('forensic_challenges'))
    
    # Get challenge description
    desc_path = os.path.join(challenge_dir, 'description.txt')
    description = "No description available."
    if os.path.exists(desc_path):
        with open(desc_path, 'r') as f:
            description = f.read()
    
    # Get challenge files
    files = []
    for filename in os.listdir(challenge_dir):
        if filename != 'description.txt' and os.path.isfile(os.path.join(challenge_dir, filename)):
            files.append(filename)
    
    return render_template('challenge.html', 
                         challenge_id=challenge_id,
                         challenge_name=challenge_id.replace('_', ' ').title(),
                         description=description,
                         files=files)

@app.route('/download_challenge_file/<challenge_id>/<filename>')
def download_challenge_file(challenge_id, filename):
    """Download a challenge file"""
    try:
        safe_path = safe_join('challenges', challenge_id, filename)
        if not os.path.exists(safe_path) or not os.path.isfile(safe_path):
            flash('File not found!', 'error')
            return redirect(url_for('challenge', challenge_id=challenge_id))
        
        return send_file(safe_path, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"File download error: {str(e)}")
        flash('Failed to download file', 'error')
        return redirect(url_for('challenge', challenge_id=challenge_id))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)