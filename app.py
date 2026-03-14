from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/happy')
def happy():
    # URL do GIF do gato "Happy Happy Happy"
    gif_url = "https://i.makeagif.com/media/12-31-2023/iFU7lY.gif"
    
    # Template HTML simples para centralizar e exibir o GIF
    html_content = f'''
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Happy Happy Happy!</title>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f0f0;
            }}
            img {{
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
        </style>
    </head>
    <body>
        <img src="{gif_url}" alt="Happy Happy Happy Cat">
    </body>
    </html>
    '''
    return render_template_string(html_content)

if __name__ == '__main__':
    # Roda o servidor em modo debug
    app.run(debug=True, port=5000)
