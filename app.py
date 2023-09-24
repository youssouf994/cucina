from flask import Flask
from flask import render_template, redirect, request, url_for, g, session, flash
from functools import wraps
import bcrypt
import sqlite3
import secrets


app = Flask(__name__)
app.secret_key='super_secret_key'


global id_corso_carrello
global id_utente


DATABASE = 'archivio_utenti.db'

def db_utenti():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

#------------------------------------------------------------------------------

"""def controllo_user():
        database_ram=db_utenti()
        cursore=database_ram.cursor()
"""

#-----------------------------------------------------------------------------

def aggiunta_carta(sessione, numero):

    database_ram=db_utenti()
    cursore=database_ram.cursor()

    if sessione is not None:
        cursore.execute('UPDATE utenti SET n_cart=? WHERE id_utente=? ', (numero, sessione))
        database_ram.commit()
        database_ram.close()

#-------------------------------------------------------------------------------


def visualizza_tutti_corsi():
    db_ram=db_utenti()
    cursore=db_ram.cursor()

    cursore.execute('SELECT * FROM service')
    corsi=cursore.fetchall()

    db_ram.close()

    return corsi

#-------------------------------------------------------------------------------

def visualizza_un_corso(id):
    db_ram=db_utenti()
    cursore=db_ram.cursor()

    cursore.execute('SELECT * FROM service WHERE id_service=?', (id,))
    corsi=cursore.fetchone()

    db_ram.close()

    return corsi


#------------------------------------------------------------------------


def elimina_riga(db_ram, id, tabella):
    """la funzione non apre il database perchè verrebbe già aperto dalla funzione
    db_utenti, quindi passo l'oggetto come parametro e lo utilizzo direttamente"""
    
    try:
        cursore=db_ram.cursor()

        cursore.execute(f"DELETE FROM {tabella} WHERE id_service=?", (id,))
        db_ram.commit()
        
        return True

    except Exception as e:
        return render_template("no.html")


#----------------------------------------------------------------------------

def modifica_elemento(db_ram, id, tabella, colonna, nuovo):
    try:
        cursore=db_ram.cursor()

        cursore.execute(f"UPDATE {tabella} SET {colonna}=? WHERE id_service=?", (nuovo, id))
        db_ram.commit()
        
        a=1
        return a

    except Exception as e:
        return render_template("no.html")

#----------------------------------------------------------------------------


def aggiungi_corso(db_ram, tabella, nome, mod, prezzo, quanti, descrizione, immag ):
    try:
        cursore=db_ram.cursor()

        cursore.execute(f"INSERT INTO {tabella} (nome, modalit, prezzo, stock, descrizione, img) VALUES (?, ?, ?, ?, ?, ?)", (nome, mod, prezzo, quanti, descrizione, immag ))
        db_ram.commit()
        
        return True

    except Exception as e:
        return render_template("no.html")


#---------------------------------------------------------------------------------

def cerca_corso(db, rif):
    
    cursore=db.cursor()

    cursore.execute("SELECT * FROM service WHERE id=?", (rif,))
    trovato=cursor.fetchone()
    

    return rif


#---------------------------------------------------------------------------------

def visualizza_carrello(db_ram, id, tabella):
    cursore=db_ram.cursor()

    cursore.execute(f"SELECT * FROM {tabella} WHERE id_uten={id}")
    carrello=cursore.fetchall()

    return carrello


#---------------------------------------------------------------------------------------

"""
wsgi_app = app.wsgi_app

usa la stringa sopra se usi un server http diverso da flask
"""


#------------------------------------------------------------------------------
#--------------------------------------FLASK------------------------------------
#------------------------------------------------------------------------------
#--------------------------------------\--/------------------------------------
#---------------------------------------\/------------------------------------
#-----------------------------------------------------------------------------|

def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'id_utenti' in session:
            return view_func(*args, **kwargs)
        else:
            return redirect(url_for('no'))
    return wrapped_view



@app.route('/no', methods=['POST', 'GET'])
def no():
    return render_template('no.html')


@app.route('/presa_carta', methods=['POST', 'GET'])
def carta():
    id=session['id_utenti']
    if request.method=='POST':
        carta=request.form['card']

        aggiunta_carta(id, carta)

        return redirect(url_for('landing'))

    return render_template('carta.html')


@app.route('/')
def index():
    """Renders a sample page."""
    corsi=visualizza_tutti_corsi()
    return render_template('index.html', corso_singolo=corsi)


@app.route('/reg')
def pag_registrazione():
    return render_template('registrazione.html')

@app.route('/log')
def login():
    return render_template('login.html')

@app.route('/stream', methods=['POST', 'GET'])

def stre():
    video = request.args.get('id_video')

    db_ram=db_utenti()
    cursore=db_ram.cursor()

    cursore.execute('SELECT * FROM service WHERE link=?', (video,))
    link=cursore.fetchone()

    link=link[7]

    db_ram.close()

    return render_template("stream.html", link=link)



@app.route('/registrazione', methods=['POST', 'GET']) 
def crea_utente():
    if request.method=='POST':
        nome=request.form['nome']
        cognome=request.form['cognome']
        tel=request.form['tel']
        citta=request.form['citt']
        mail=request.form['mail']
        passw=request.form['pass']

        data=db_utenti()
        cursore=data.cursor()


        cursore.execute('SELECT * FROM utenti WHERE cell=?', (tel,))
        if cursore.fetchone() is not None:
           return redirect(url_for('no'))
        else:
            #-----------CODIFICA VALORI INSERITI--------------
            pass_codificata=bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt())
            #mail_codificata=bcrypt.hashpw(mail.encode('utf-8'), bcrypt.gensalt())
            #tel_codificata=bcrypt.hashpw(tel.encode('utf-8'), bcrypt.gensalt())
            #city_codificata=bcrypt.hashpw(citta.encode('utf-8'), bcrypt.gensalt())
            #cognome_codificata=bcrypt.hashpw(cognome.encode('utf-8'), bcrypt.gensalt())
            #nome_codificata=bcrypt.hashpw(nome.encode('utf-8'), bcrypt.gensalt())
            #-----------------------------------------------------------

            cursore.execute('INSERT INTO utenti (nome, cognome, mail, citta, cell, passwo) VALUES (?, ?, ?, ?, ?, ?)',
                            (nome, cognome, mail, citta, tel, pass_codificata ))
            
            data.commit()
            data.close()

            return render_template('index.html')

    return render_template('registrazione.html')


@app.route('/login', methods=['POST', 'GET'])
def accesso():
    global id_utente
    trovato_nome=None
    if request.method=='POST':
        utente=request.form['user']
        passwd=request.form['pass'].encode('UTF-8')

        database_ram=db_utenti()
        cursore=database_ram.cursor()

        cursore.execute('SELECT * FROM utenti WHERE nome=?', (utente,))
        trovato_nome=cursore.fetchone()

        database_ram.close()
        
        creator=trovato_nome[1]
        creator=creator[:5]
        numero="ad458"
        print(creator,"   ",numero)


    if ((trovato_nome is not None and bcrypt.checkpw(passwd, trovato_nome[7]) and
          (creator==numero))):
        session['id_utente']=trovato_nome[0]
        id_utente=session['id_utente']
        #trovato_nome=None
        return redirect(url_for('dashboard_creators'))

    elif trovato_nome is not None and bcrypt.checkpw(passwd, trovato_nome[7]):
        session['id_utenti']=trovato_nome[0]
        id_utente=session['id_utenti']
        #trovato_nome=None
        return redirect(url_for('landing'))
           
    else:
        trovato_nome=None
        return redirect(url_for('no'))        


@app.route('/land', methods=['POST', 'GET'])
@login_required
def landing():
    corsi=visualizza_tutti_corsi()

    return render_template('landing_page.html', corso_singolo=corsi)


@app.route('/cucina_africana/<int:id_corso>')
def panoramica(id_corso):
    global id_corso_carrello
    corso=visualizza_un_corso(id_corso)
    id_corso_carrello=id_corso
    return render_template('pano.html', corso=corso)


@app.route('/carrello2', methods=['POST', 'GET']) 
@login_required
def vis_carrello():
    if 'id_utente' not in globals():
        msg="Prima effettuare il login"

        return render_template("index.html", msg=msg)

    else:
        id=id_utente
        tabella="carrello"
        db=db_utenti()
        acquistati=visualizza_carrello(db, id, tabella)
        tot=0
        for acquisto in acquistati:
            tot+=float(acquisto[4])

        return render_template("carrello.html", acquistati=acquistati, tot=tot)



@app.route('/carrello', methods=['POST', 'GET'])
@login_required
def carrello():
    global id_corso_carrello
    global id_utente
    
    if request.method=='POST':
        quant=request.form['quanti']
        


    if 'id_utenti' in session and id_corso_carrello != None:
        dati = db_utenti()
        cursore = dati.cursor()
        try:
            #prendo il oprezzo dalla tabella corsi
            cursore.execute('SELECT prezzo FROM service WHERE id_service=?', (id_corso_carrello,))
            prezzo=cursore.fetchone()[0]#CURSORE NON è NE UNA LISTA NE UNA TUPLA FACENDO FETCHONE HA UN UNICO VALORE SE AUMENTI L'INDICE < 0 VAI OUT OF RANGE 
            float(prezzo)
            prezzo*=float(quant)

            #prendo il nome del corso dalla tab corsi
            cursore.execute('SELECT nome FROM service WHERE id_service=?', (id_corso_carrello,))
            nome_corso=cursore.fetchone()[0]#CURSORE NON è NE UNA LISTA NE UNA TUPLA FACENDO FETCHONE HA UN UNICO VALORE SE AUMENTI L'INDICE < 0 VAI OUT OF RANGE

            #Inserisco il corso e i dati nel carrello dell'utente
            cursore.execute('INSERT INTO carrello (id_prodotto, id_uten, quantita, prezzo_unitario, nome_prodotto) VALUES (?, ?, ?, ?, ?) ', (id_corso_carrello, id_utente, quant, prezzo, nome_corso,))
            dati.commit()

        except Exception as e:
            dati.rollback()
            return render_template("no.html")
            
        finally:
            dati.close()


        #resetta le variabili globali
        id_corso_carrello = None
        

        return redirect(url_for('vis_carrello'))
    else:
        return "Errore: ID corso o ID utente mancanti."





@app.route('/nuovo', methods=['POST', 'GET'])
@login_required
def nuovo_corso():
    if request.method=='POST':
        tabe="service"
        nom=request.form['nome']
        modal=request.form['dalit']
        soldi=request.form['prez']
        descri=request.form['descr']
        in_vendita=request.form['num']
        immagine=request.form['img']

        soldi=float(soldi)

        db=db_utenti()

        aggiungi_corso(db, tabe, nom, modal, soldi, in_vendita, descri, immagine)


        db.close()

        return render_template('dash_creators.html')


@app.route('/pano_creators', methods=['POST', 'GET'])
@login_required
def visualizza_creators():
    corsi=visualizza_tutti_corsi()
    return render_template('dash_creators.html', corsi=corsi)


@app.route('/modifica', methods=['POST'])
def mod_corso():
    if session is not None:
        valore=request.form.getlist('cod')
        selezionato=request.form['quale']
        modificato=request.form['nuovo']

        db=db_utenti()
        try:
            if 'co' in valore:
                a=modifica_elemento(db, selezionato, 'service', 'nome', modificato)


            elif 'mod' in valore:
                modifica_elemento(db, selezionato, "service", "modalit", modificato)

            elif 'prez' in valore:
                modificato=float(modificato)
                modifica_elemento(db, selezionato, "service", "prezzo", modificato)

            elif 'quanti' in valore:
                modificato=int(modificato)
                modifica_elemento(db, selezionato, "service", "stock", modificato)

            elif 'desc' in valore:
                modifica_elemento(db, selezionato, "service", "descrizione", modificato)

            elif 'imge' in valore:
                modifica_elemento(db, selezionato, "service", "img", modificato)

        except Exception as e:
            return redirect(url_for('no'))

        finally:
            db.close()
    
    
        return render_template('dash_creators.html')
    
    else:
        return render_template('no.html')


@app.route('/elimina', methods=['POST'])
def elimina():
    quale=request.form['elimino']

    if session is not None:    
        db=db_utenti()

        try:
            elimina_riga(db, quale, "service")

        except Exception as e:
            return redirect(url_for('no'))

        finally:
            db.close()

        return render_template('dash_creators.html')
    
    else:
        return redirect(url_for('no'))


@app.route('/creators', methods=['POST', 'GET'])
@login_required
def dashboard_creators():
    if request.method=='POST':
        return render_template('dash_creators.html')
    return render_template('dash_creators.html')


@app.route('/elimina_riga', methods=['GET'])
def elimina_riga():
    id77 = request.args.get('id77')
    if id77:
        # Ora hai l'ID da eliminare, puoi eseguire una query di eliminazione
        db_ram = db_utenti()
        cursor = db_ram.cursor()
        cursor.execute("DELETE FROM carrello WHERE id = ?", (id77,))
        db_ram.commit()
        db_ram.close()

    return redirect(url_for('vis_carrello'))

"""
    MODIFICARE IL CODICE SOTTOSTANTE PRIMA DI ESEGUIRE IL DEBUG IN PARTICOLARE IL NUMERO DELLA PORTA.
    DOVREBBE ESSERE app.run(host='0.0.0.0', port=xxxx)
"""

if __name__ == '__main__':#parte esecuzione dal file non da codice importato da altro file
    import os#libreria che mi da accesso alle variabili d'ambiente del sist operativo
    HOST = os.environ.get('SERVER_HOST', 'localhost')#prendo la var che contiene host
    try:
        PORT = int(os.environ.get('SERVER_PORT', '4000'))#provo a connettermi alla seguente
    except ValueError:
        PORT = 4000#se c'è un errore passo alla seguente
    app.run(HOST, PORT)#app.run finalizza il codice soprastante