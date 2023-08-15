from colorama import Cursor
from flask import Flask, render_template, request ,redirect,url_for,flash 
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= ''
app.config['MYSQL_DB']= 'dbcontabiliapp'
mysql= MySQL(app)
app.secret_key='mysecretkey'

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/vw_insertFormatos',methods=['POST'])
def vwInsertFormatos():
    if request.method == ('POST'):
        formato = request.form['formato']
        print(formato)
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO formatos(nombre)values(%s)',[formato])
        mysql.connection.commit()

        cursos=mysql.connection.cursor()
        cursos.execute('SELECT * FROM formatos WHERE nombre= %s',[formato])
        consulta = cursos.fetchall()
        print(consulta)
        return render_template('Become.html', Formato= consulta)


@app.route('/vw_insertDatos/<idFormato>')
def vwInsertDatos(idFormato):
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formatos WHERE id_formato= %s',[idFormato])
    consulta = cur.fetchall()
    cur1=mysql.connection.cursor()
    cur1.execute('SELECT * FROM conceptos')
    consulta1 = cur1.fetchall()
    cur2=mysql.connection.cursor()
    cur2.execute('SELECT * FROM deberhaber')
    consulta2 = cur2.fetchall()
    cur3=mysql.connection.cursor()
    cur3.execute('SELECT * FROM datos JOIN conceptos ON datos.concepto_id = conceptos.id_concepto JOIN deberhaber ON datos.deberHaber_id = deberhaber.id_deberHaber WHERE formato_id= %s',[idFormato])
    consulta3 = cur3.fetchall()
    return render_template('vwInsertDatos.html',consulta=consulta,conceptos=consulta1, deberhaber=consulta2, idFormato=idFormato, datos= consulta3)

@app.route('/vw_insertData/<idFormato>',methods=['POST'])
def vwInsertData(idFormato):
    if request.method == ('POST'):
        monto = request.form['monto']
        print(monto)
        Concepto = request.form['Concepto']
        print(Concepto)
        tipo = request.form['tipo']
        print(tipo)
        cur1=mysql.connection.cursor()
        cur1.execute('INSERT INTO datos(monto,concepto_id,deberHaber_id,formato_id) values(%s,%s,%s, %s)',[monto,Concepto,tipo,idFormato])
        mysql.connection.commit()
        return redirect(url_for('vwInsertDatos',idFormato=idFormato)) 


@app.route('/vw_esquemaT/<idFormato>')
def vwEsquemaT(idFormato):
    dataEsquemasT=mysql.connection.cursor()
    dataEsquemasT.execute('SELECT datos.id_dato, datos.monto, datos.deberHaber_id, conceptos.id_Concepto FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s',[idFormato])
    mysql.connection.commit()
    conjuntoDatos = dataEsquemasT.fetchall()

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formatos WHERE id_formato= %s',[idFormato])
    consulta = cur.fetchone()
    cur=mysql.connection.cursor()

    #SUMAS DE BANCOS
    sumaAbonoBa = mysql.connection.cursor()
    sumaAbonoBa.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=2',[idFormato])
    resultado = sumaAbonoBa.fetchone()
    sumaAbonoBa=mysql.connection.cursor()

    if resultado is not None:#Comprueba si viene vacio
        sumaAbonoBanco = resultado[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")

    sumaCargoBa = mysql.connection.cursor()
    sumaCargoBa.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=2',[idFormato])
    resultado = sumaCargoBa.fetchone()
    sumaCargoBa=mysql.connection.cursor()
    totalBancos = 0 
    if resultado is not None:
        sumaCargoBanco = resultado[0]
    else:
        print("No se encontraron resultados.") 

    if sumaAbonoBanco > sumaCargoBanco or sumaAbonoBanco == sumaCargoBanco:
        if sumaAbonoBanco is not None and sumaCargoBanco is not None:
            totalBancos=sumaAbonoBanco-sumaCargoBanco #RESTA DE ABONO Y CARGO

        else:
            print("Uno o ambos valores son None.")
    else:
        if sumaAbonoBanco is not None and sumaCargoBanco is not None:
            totalBancos=sumaCargoBanco-sumaAbonoBanco #RESTA DE ABONO Y CARGO

        else:
            print("Uno o ambos valores son None.")
    

    #AQUI DEBERIA INICIAR SUMA DE INVERSIONES TEMPORALES
     #SUMAS DE CAJA
    sumaAbonoCa = mysql.connection.cursor()
    sumaAbonoCa.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=1',[idFormato])
    resultadoCa = sumaAbonoCa.fetchone()
    sumaAbonoCa=mysql.connection.cursor()

    if resultadoCa is not None:#Comprueba si viene vacio
        sumaAbonoCajas= resultadoCa[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")

    sumaCargoCa = mysql.connection.cursor()
    sumaCargoCa.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=1',[idFormato])
    resultadoCa = sumaCargoCa.fetchone()
    sumaCargoCa=mysql.connection.cursor()
    totalCajas = 0 
    if resultadoCa is not None:
        sumaCargoCajas = resultadoCa[0]
    else:
        print("No se encontraron resultados.")

    if sumaAbonoCajas is not None and sumaCargoCajas is not None:
        totalCajas = sumaCargoCajas-sumaAbonoCajas
    else:
        print("Uno o ambos valores son None.")

    #SUMAS DE Inversiones
    sumaAbonoIn = mysql.connection.cursor()
    sumaAbonoIn.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=3',[idFormato])
    resultadoIn = sumaAbonoIn.fetchone()
    sumaAbonoIn=mysql.connection.cursor()

    if resultadoIn is not None:#Comprueba si viene vacio
        sumaAbonoInversiones = resultadoIn[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalInversiones=0
    sumaCargoIn = mysql.connection.cursor()
    sumaCargoIn.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=3',[idFormato])
    resultadoIn = sumaCargoIn.fetchone()
    sumaCargoIn=mysql.connection.cursor()
    if resultadoIn is not None:
        sumaCargoInversiones = resultadoIn[0]
    else:
        print("No se encontraron resultados.")

    if sumaAbonoInversiones is not None and sumaCargoInversiones is not None:
        totalInversiones=sumaCargoInversiones-sumaAbonoInversiones
    else:
        print("Uno o ambos valores son None.")


   

     #SUMAS DE ALMACENES
    sumaAbonoAL = mysql.connection.cursor()
    sumaAbonoAL.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=4',[idFormato])
    resultadoAL = sumaAbonoAL.fetchone()
    sumaAbonoAL=mysql.connection.cursor()

    if resultadoAL is not None:#Comprueba si viene vacio
        sumaAbonoAlmacenes = resultadoAL[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalAlmacenes=0
    sumaCargoAL = mysql.connection.cursor()
    sumaCargoAL.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=4',[idFormato])
    resultadoAL = sumaCargoAL.fetchone()
    sumaCargoAL=mysql.connection.cursor()
    if resultadoAL is not None:
        sumaCargoAlmacenes  = resultadoAL[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoAlmacenes is not None and sumaCargoAlmacenes is not None:
        totalAlmacenes = sumaCargoAlmacenes -sumaAbonoAlmacenes
    else:
        print("Uno o ambos valores son None.")
     

     #SUMAS DE Clientes 
    sumaAbonoCl = mysql.connection.cursor()
    sumaAbonoCl.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=5',[idFormato])
    resultadoCl = sumaAbonoCl.fetchone()
    sumaAbonoCl=mysql.connection.cursor()

    if resultadoCl is not None:#Comprueba si viene vacio
        sumaAbonoClientes = resultadoCl[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalClientes=0
    sumaCargoCl = mysql.connection.cursor()
    sumaCargoCl.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=5',[idFormato])
    resultadoCl = sumaCargoCl.fetchone()
    sumaCargoCl=mysql.connection.cursor()
    if resultadoCl is not None:
        sumaCargoClientes  = resultadoCl[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoClientes is not None and sumaCargoClientes is not None:
        totalClientes =sumaCargoClientes- sumaAbonoClientes
    else:
        print("Uno o ambos valores son None.")
     

     #SUMAS DE DocumentosC
    sumaAbonoDC = mysql.connection.cursor()
    sumaAbonoDC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=6',[idFormato])
    resultadoDC = sumaAbonoDC.fetchone()
    sumaAbonoDC=mysql.connection.cursor()

    if resultadoDC is not None:#Comprueba si viene vacio
        sumaAbonoDocumentosC= resultadoDC[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalDocumentosC=0
    sumaCargoDC = mysql.connection.cursor()
    sumaCargoDC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=6',[idFormato])
    resultadoDC = sumaCargoDC.fetchone()
    sumaCargoDC=mysql.connection.cursor()
    if resultadoDC is not None:
        sumaCargoDocumentosC = resultadoDC[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoDocumentosC is not None and sumaCargoDocumentosC is not None:
        totalDocumentosC=sumaCargoDocumentosC - sumaAbonoDocumentosC
    else:
        print("Uno o ambos valores son None.")
    

     #SUMAS DE DeudoresD
    sumaAbonoDD = mysql.connection.cursor()
    sumaAbonoDD.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=7',[idFormato])
    resultadoDD = sumaAbonoDD.fetchone()
    sumaAbonoDD=mysql.connection.cursor()

    if resultadoDD is not None:#Comprueba si viene vacio
        sumaAbonoDeudoresD= resultadoDD[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalDeudoresD=0
    sumaCargoDD = mysql.connection.cursor()
    sumaCargoDD.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=7',[idFormato])
    resultadoDD = sumaCargoDD.fetchone()
    sumaCargoDD=mysql.connection.cursor()
    if resultadoDD is not None:
        sumaCargoDeudoresD = resultadoDD[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoDeudoresD is not None and sumaCargoDeudoresD is not None:
        totalDeudoresD=sumaCargoDeudoresD-sumaAbonoDeudoresD
    else:
        print("Uno o ambos valores son None.")
   

     #SUMAS DE AnticipoP
    sumaAbonoAP = mysql.connection.cursor()
    sumaAbonoAP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=8',[idFormato])
    resultadoAP = sumaAbonoAP.fetchone()
    sumaAbonoAP=mysql.connection.cursor()

    if resultadoAP is not None:#Comprueba si viene vacio
        sumaAbonoAnticipoP= resultadoAP[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalAnticipoP=0
    sumaCargoAP = mysql.connection.cursor()
    sumaCargoAP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=8',[idFormato])
    resultadoAP = sumaCargoAP.fetchone()
    sumaCargoAP=mysql.connection.cursor()
    if resultadoAP is not None:
        sumaCargoAnticipoP = resultadoAP[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoAnticipoP is not None and sumaCargoAnticipoP is not None:
        totalAnticipoP=sumaCargoAnticipoP- sumaAbonoAnticipoP
    else:
        print("Uno o ambos valores son None.")
    

     #SUMAS DE Terreno
    sumaAbonoTE = mysql.connection.cursor()
    sumaAbonoTE.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=9',[idFormato])
    resultadoTE = sumaAbonoTE.fetchone()
    sumaAbonoTE=mysql.connection.cursor()

    if resultadoTE is not None:#Comprueba si viene vacio
        sumaAbonoTerreno= resultadoTE[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalTerreno=0
    sumaCargoTE = mysql.connection.cursor()
    sumaCargoTE.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=9',[idFormato])
    resultadoTE = sumaCargoTE.fetchone()
    sumaCargoTE=mysql.connection.cursor()
    if resultadoTE is not None:
        sumaCargoTerreno= resultadoTE[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoTerreno is not None and sumaCargoTerreno is not None:
        totalTerreno=sumaCargoTerreno-sumaAbonoTerreno
    else:
        print("Uno o ambos valores son None.")
    

     #SUMAS DE Edificios
    sumaAbonoED = mysql.connection.cursor()
    sumaAbonoED.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=10',[idFormato])
    resultadoED = sumaAbonoED.fetchone()
    sumaAbonoED=mysql.connection.cursor()

    if resultadoED is not None:#Comprueba si viene vacio
        sumaAbonoEdificios= resultadoED[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalEdificios=0
    sumaCargoED = mysql.connection.cursor()
    sumaCargoED.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=10',[idFormato])
    resultadoED = sumaCargoED.fetchone()
    sumaCargoED=mysql.connection.cursor()
    if resultadoED is not None:
        sumaCargoEdificios = resultadoED[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoEdificios is not None and sumaCargoEdificios is not None:
        totalEdificios=sumaCargoEdificios-sumaAbonoEdificios
    else:
        print("Uno o ambos valores son None.")
    
    ####
    #SUMAS DE Mobiliarios
    sumaAbonoMO = mysql.connection.cursor()
    sumaAbonoMO.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=11',[idFormato])
    resultadoMO = sumaAbonoMO.fetchone()
    sumaAbonoMO=mysql.connection.cursor()

    if resultadoMO is not None:#Comprueba si viene vacio
        sumaAbonoMobiliarios= resultadoMO[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalMobiliarios=0
    sumaCargoMO = mysql.connection.cursor()
    sumaCargoMO.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=11',[idFormato])
    resultadoMO = sumaCargoMO.fetchone()
    sumaCargoMO=mysql.connection.cursor()
    if resultadoMO is not None:
        sumaCargoMobiliarios = resultadoMO[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoMobiliarios is not None and sumaCargoMobiliarios is not None:
        totalMobiliarios=sumaCargoMobiliarios-sumaAbonoMobiliarios
    else:
        print("Uno o ambos valores son None.")
   
    #SUMAS DE EquipoC
    sumaAbonoEC = mysql.connection.cursor()
    sumaAbonoEC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=12',[idFormato])
    resultadoEC = sumaAbonoEC.fetchone()
    sumaAbonoEC=mysql.connection.cursor()

    if resultadoEC is not None:#Comprueba si viene vacio
        sumaAbonoEquipoC= resultadoEC[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalEquipoC=0
    sumaCargoEC = mysql.connection.cursor()
    sumaCargoEC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=12',[idFormato])
    resultadoEC = sumaCargoEC.fetchone()
    sumaCargoEC=mysql.connection.cursor()
    if resultadoEC is not None:
        sumaCargoEquipoC = resultadoEC[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoEquipoC is not None and sumaCargoEquipoC is not None:
        totalEquipoC=sumaCargoEquipoC-sumaAbonoEquipoC
    else:
        print("Uno o ambos valores son None.")

    #SUMAS DE EquipoE
    sumaAbonoEE = mysql.connection.cursor()
    sumaAbonoEE.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=13',[idFormato])
    resultadoEE = sumaAbonoEE.fetchone()
    sumaAbonoEE=mysql.connection.cursor()

    if resultadoEE is not None:#Comprueba si viene vacio
        sumaAbonoEquipoE = resultadoEE[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalEquipoE=0
    sumaCargoEE = mysql.connection.cursor()
    sumaCargoEE.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=13',[idFormato])
    resultadoEE = sumaCargoEE.fetchone()
    sumaCargoEE=mysql.connection.cursor()
    if resultadoEE is not None:
        sumaCargoEquipoE = resultadoEE[0]
    else:
        print("No se encontraron resultados.")
    if sumaAbonoEquipoE is not None and sumaCargoEquipoE is not None:
        totalEquipoE=sumaCargoEquipoE-sumaAbonoEquipoE
    else:
        print("Uno o ambos valores son None.")


     #SUMAS DE DepositoG
    sumaAbonoDG = mysql.connection.cursor()
    sumaAbonoDG.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=14',[idFormato])
    resultadoDG = sumaAbonoDG.fetchone()
    sumaAbonoDG=mysql.connection.cursor()

    if resultadoDG is not None:#Comprueba si viene vacio
        sumaAbonoDepositoG = resultadoDG[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalDepositoG=0
    sumaCargoDG = mysql.connection.cursor()
    sumaCargoDG.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=14',[idFormato])
    resultadoDG = sumaCargoDG.fetchone()
    sumaCargoDG=mysql.connection.cursor()
    if resultadoDG is not None:
        sumaCargoDepositoG  = resultadoDG[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoDepositoG is not None and sumaCargoDepositoG is not None:
        totalDepositoG =sumaCargoDepositoG-sumaAbonoDepositoG
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE InversionP 
    sumaAbonoIP = mysql.connection.cursor()
    sumaAbonoIP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=15',[idFormato])
    resultadoIP = sumaAbonoIP.fetchone()
    sumaAbonoIP=mysql.connection.cursor()

    if resultadoIP is not None:#Comprueba si viene vacio
        sumaAbonoInversionP= resultadoIP[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalInversionP=0
    sumaCargoIP = mysql.connection.cursor()
    sumaCargoIP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=15',[idFormato])
    resultadoIP = sumaCargoIP.fetchone()
    sumaCargoIP=mysql.connection.cursor()
    if resultadoIP is not None:
        sumaCargoInversionP  = resultadoIP[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoInversionP is not None and sumaCargoInversionP is not None:
        totalInversionP =sumaCargoInversionP-sumaAbonoInversionP
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE GastosI
    sumaAbonoGI = mysql.connection.cursor()
    sumaAbonoGI.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=16',[idFormato])
    resultadoGI = sumaAbonoGI.fetchone()
    sumaAbonoGI=mysql.connection.cursor()

    if resultadoGI is not None:#Comprueba si viene vacio
        sumaAbonoGastosI= resultadoGI[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalGastosI=0
    sumaCargoGI = mysql.connection.cursor()
    sumaCargoGI.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=16',[idFormato])
    resultadoGI = sumaCargoGI.fetchone()
    sumaCargoGI=mysql.connection.cursor()
    if resultadoDC is not None:
        sumaCargoGastosI = resultadoGI[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoGastosI is not None and sumaCargoGastosI is not None:  
        totalGastosI=sumaCargoGastosI-sumaAbonoGastosI
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE GastosE
    sumaAbonoGE = mysql.connection.cursor()
    sumaAbonoGE.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=17',[idFormato])
    resultadoGE = sumaAbonoGE.fetchone()
    sumaAbonoGE=mysql.connection.cursor()

    if resultadoGE is not None:#Comprueba si viene vacio
        sumaAbonoGastosE= resultadoGE[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalGastosE=0
    sumaCargoGE = mysql.connection.cursor()
    sumaCargoGE.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=17',[idFormato])
    resultadoGE = sumaCargoGE.fetchone()
    sumaCargoGE=mysql.connection.cursor()
    if resultadoGE is not None:
        sumaCargoGastosE = resultadoGE[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoGastosE is not None and sumaCargoGastosE is not None:  
        totalGastosE=sumaCargoGastosE-sumaAbonoGastosE
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE GastosM
    sumaAbonoGM = mysql.connection.cursor()
    sumaAbonoGM.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=18',[idFormato])
    resultadoGM = sumaAbonoGM.fetchone()
    sumaAbonoGM=mysql.connection.cursor()

    if resultadoGM is not None:#Comprueba si viene vacio
        sumaAbonoGastosM= resultadoGM[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalGastosM=0
    sumaCargoGM = mysql.connection.cursor()
    sumaCargoGM.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=18',[idFormato])
    resultadoGM = sumaCargoGM.fetchone()
    sumaCargoGM=mysql.connection.cursor()
    if resultadoGM is not None:
        sumaCargoGastosM = resultadoGM[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoGastosM is not None and sumaCargoGastosM is not None:
        totalGastosM=sumaCargoGastosM-sumaAbonoGastosM
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE GastosO
    sumaAbonoGO = mysql.connection.cursor()
    sumaAbonoGO.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=19',[idFormato])
    resultadoGO = sumaAbonoGO.fetchone()
    sumaAbonoGO=mysql.connection.cursor()

    if resultadoGO is not None:#Comprueba si viene vacio
        sumaAbonoGastosO= resultadoGO[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalGastosO=0
    sumaCargoGO = mysql.connection.cursor()
    sumaCargoGO.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=19',[idFormato])
    resultadoGO = sumaCargoGO.fetchone()
    sumaCargoGO=mysql.connection.cursor()
    if resultadoGO is not None:
        sumaCargoGastosO = resultadoGO[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoGastosO is not None and sumaCargoGastosO is not None: 
        totalGastosO=sumaCargoGastosO-sumaAbonoGastosO
    else:
        print("Uno o ambos valores son None.")

         #SUMAS DE GastosIn
    sumaAbonoGIN = mysql.connection.cursor()
    sumaAbonoGIN.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=20',[idFormato])
    resultadoGIN = sumaAbonoGIN.fetchone()
    sumaAbonoGIN=mysql.connection.cursor()

    if resultadoGIN is not None:#Comprueba si viene vacio
        sumaAbonoGastosIn= resultadoGIN[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalGastosIn=0
    sumaCargoGIN = mysql.connection.cursor()
    sumaCargoGIN.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=20',[idFormato])
    resultadoGIN = sumaCargoGIN.fetchone()
    sumaCargoGIN=mysql.connection.cursor()
    if resultadoGIN is not None:
        sumaCargoGastosIn = resultadoGIN[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoGastosIn is not None and sumaCargoGastosIn is not None:
        
        totalGastosIn=sumaCargoGastosIn-sumaAbonoGastosIn
    else:
        print("Uno o ambos valores son None.")

    #SUMAS DE Papeleria
    sumaAbonoPA = mysql.connection.cursor()
    sumaAbonoPA.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=21',[idFormato])
    resultadoPA = sumaAbonoPA.fetchone()
    sumaAbonoPA=mysql.connection.cursor()

    if resultadoPA is not None:#Comprueba si viene vacio
        sumaAbonoPapeleria= resultadoPA[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalPapeleria=0
    sumaCargoPA = mysql.connection.cursor()
    sumaCargoPA.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=21',[idFormato])
    resultadoPA = sumaCargoPA.fetchone()
    sumaCargoPA=mysql.connection.cursor()
    if resultadoPA is not None:
        sumaCargoPapeleria = resultadoPA[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoPapeleria is not None and sumaCargoPapeleria is not None:

        totalPapeleria=sumaCargoPapeleria-sumaAbonoPapeleria
    else:
        print("Uno o ambos valores son None.")

    #SUMAS DE Propaganda
    sumaAbonoPR = mysql.connection.cursor()
    sumaAbonoPR.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=22',[idFormato])
    resultadoPR = sumaAbonoPR.fetchone()
    sumaAbonoPR=mysql.connection.cursor()

    if resultadoPR is not None:#Comprueba si viene vacio
        sumaAbonoPropaganda = resultadoPR[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalPropaganda=0
    sumaCargoPR = mysql.connection.cursor()
    sumaCargoPR.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=22',[idFormato])
    resultadoPR = sumaCargoPR.fetchone()
    sumaCargoPR=mysql.connection.cursor()
    if resultadoPR is not None:
        sumaCargoPropaganda = resultadoPR[0]
    else:
        print("No se encontraron resultados.")
    if sumaAbonoPropaganda is not None and sumaCargoPropaganda is not None:
        totalPropaganda=sumaCargoPropaganda-sumaAbonoPropaganda   
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE PrimasS
    sumaAbonoPS = mysql.connection.cursor()
    sumaAbonoPS.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=23',[idFormato])
    resultadoPS = sumaAbonoPS.fetchone()
    sumaAbonoAL=mysql.connection.cursor()

    if resultadoPS is not None:#Comprueba si viene vacio
        sumaAbonoPrimasS = resultadoPS[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalPrimasS=0
    sumaCargoPS = mysql.connection.cursor()
    sumaCargoPS.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=23',[idFormato])
    resultadoPS = sumaCargoPS.fetchone()
    sumaCargoPS=mysql.connection.cursor()
    if resultadoPS is not None:
        sumaCargoPrimasS  = resultadoPS[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoPrimasS is not None and sumaCargoPrimasS is not None:
        totalPrimasS =sumaCargoPrimasS-sumaAbonoPrimasS 
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE RentasP 
    sumaAbonoRP = mysql.connection.cursor()
    sumaAbonoRP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=24',[idFormato])
    resultadoRP = sumaAbonoRP.fetchone()
    sumaAbonoRP=mysql.connection.cursor()

    if resultadoRP is not None:#Comprueba si viene vacio
        sumaAbonoRentasP = resultadoRP[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalRentasP=0
    sumaCargoRP = mysql.connection.cursor()
    sumaCargoRP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=24',[idFormato])
    resultadoRP = sumaCargoRP.fetchone()
    sumaCargoRP=mysql.connection.cursor()
    if resultadoRP is not None:
        sumaCargoRentasP  = resultadoRP[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoRentasP is not None and sumaCargoRentasP is not None:
        totalRentasP =sumaCargoRentasP-sumaAbonoRentasP
    else:
        print("Uno o ambos valores son None.") 

     #SUMAS DE InteresesP
    sumaAbonoIP = mysql.connection.cursor()
    sumaAbonoIP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=25',[idFormato])
    resultadoIP = sumaAbonoIP.fetchone()
    sumaAbonoIP=mysql.connection.cursor()

    if resultadoIP is not None:#Comprueba si viene vacio
        sumaAbonoInteresesP= resultadoIP[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalInteresesP=0
    sumaCargoIP = mysql.connection.cursor()
    sumaCargoIP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=25',[idFormato])
    resultadoIP = sumaCargoIP.fetchone()
    sumaCargoIP=mysql.connection.cursor()
    if resultadoIP is not None:
        sumaCargoInteresesP = resultadoIP[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoInteresesP is not None and sumaCargoInteresesP is not None:
        totalInteresesP=sumaCargoInteresesP-sumaAbonoInteresesP
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE Proveedores 
    sumaAbonoP = mysql.connection.cursor()
    sumaAbonoP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=26',[idFormato])
    resultadoP = sumaAbonoP.fetchone()
    sumaAbonoP =mysql.connection.cursor()

    if resultadoP is not None:#Comprueba si viene vacio
        sumaAbonoProveedores = resultadoP[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalProveedores=0
    sumaCargoP = mysql.connection.cursor()
    sumaCargoP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=26',[idFormato])
    resultadoP = sumaCargoP.fetchone()
    sumaCargoP=mysql.connection.cursor()
    if resultadoP is not None:
        sumaCargoProveedores  = resultadoP[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoProveedores is not None and sumaCargoProveedores is not None:
        totalProveedores = sumaAbonoProveedores-sumaCargoProveedores 
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE DocumentosP
    sumaAbonoDP = mysql.connection.cursor()
    sumaAbonoDP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=27',[idFormato])
    resultadoDP = sumaAbonoDP.fetchone()
    sumaAbonoDP=mysql.connection.cursor()

    if resultadoDP is not None:#Comprueba si viene vacio
        sumaAbonoDocumentosP= resultadoDP[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalDocumentosP=0
    sumaCargoDP = mysql.connection.cursor()
    sumaCargoDP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=27',[idFormato])
    resultadoDP = sumaCargoDP.fetchone()
    sumaCargoDP=mysql.connection.cursor()
    if resultadoDP is not None:
        sumaCargoDocumentosP = resultadoDP[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoDocumentosP is not None and sumaCargoDocumentosP is not None:
        totalDocumentosP=sumaCargoDocumentosP-sumaAbonoDocumentosP
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE AcreedoresD
    sumaAbonoAD = mysql.connection.cursor()
    sumaAbonoAD.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=28',[idFormato])
    resultadoAD = sumaAbonoAD.fetchone()
    sumaAbonoAD=mysql.connection.cursor()

    if resultadoAD is not None:#Comprueba si viene vacio
        sumaAbonoAcreedoresD= resultadoAD[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalAcreedoresD=0
    sumaCargoAD = mysql.connection.cursor()
    sumaCargoAD.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=28',[idFormato])
    resultadoAD = sumaCargoAD.fetchone()
    sumaCargoAD=mysql.connection.cursor()
    if resultadoAD is not None:
        sumaCargoAcreedoresD= resultadoAD[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoAcreedoresD is not None and sumaCargoAcreedoresD is not None:
        totalAcreedoresD=sumaAbonoAcreedoresD-sumaCargoAcreedoresD
    else:
        print("Uno o ambos valores son None.")

     #SUMAS DE AnticipoC
    sumaAbonoAC = mysql.connection.cursor()
    sumaAbonoAC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=29',[idFormato])
    resultadoAC = sumaAbonoAC.fetchone()
    sumaAbonoAC=mysql.connection.cursor()

    if resultadoAC is not None:#Comprueba si viene vacio
        sumaAbonoAnticipoC= resultadoAC[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalAnticipoC=0
    sumaCargoAC = mysql.connection.cursor()
    sumaCargoAC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=29',[idFormato])
    resultadoAC = sumaCargoAC.fetchone()
    sumaCargoAC=mysql.connection.cursor()
    if resultadoAC is not None:
        sumaCargoAnticipoC = resultadoAC[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoAnticipoC is not None and sumaCargoAnticipoC is not None:
        totalAnticipoC=sumaCargoAnticipoC-sumaAbonoAnticipoC
    else:
        print("Uno o ambos valores son None.")

    #SUMAS DE GastosP
    sumaAbonoGP = mysql.connection.cursor()
    sumaAbonoGP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=30',[idFormato])
    resultadoGP = sumaAbonoGP.fetchone()
    sumaAbonoGP=mysql.connection.cursor()

    if resultadoGP is not None:#Comprueba si viene vacio
        sumaAbonoGastosP= resultadoGP[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalGastosP=0
    sumaCargoGP = mysql.connection.cursor()
    sumaCargoGP.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=30',[idFormato])
    resultadoGP = sumaCargoGP.fetchone()
    sumaCargoGP=mysql.connection.cursor()
    if resultadoGP is not None:
        sumaCargoGastosP = resultadoGP[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoGastosP is not None and sumaCargoGastosP is not None:
        totalGastosP=sumaCargoGastosP-sumaAbonoGastosP
    else:
        print("Uno o ambos valores son None.")

    #SUMAS DE ImpuestosP
    sumaAbonoIM = mysql.connection.cursor()
    sumaAbonoIM.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=31',[idFormato])
    resultadoIM = sumaAbonoIM.fetchone()
    sumaAbonoIM=mysql.connection.cursor()

    if resultadoIM is not None:#Comprueba si viene vacio
        sumaAbonoImpuestosP= resultadoIM[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalImpuestosP=0
    sumaCargoIM = mysql.connection.cursor()
    sumaCargoIM.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=31',[idFormato])
    resultadoIM = sumaCargoIM.fetchone()
    sumaCargoIM=mysql.connection.cursor()
    if resultadoED is not None:
        sumaCargoImpuestosP = resultadoIM[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoImpuestosP is not None and sumaCargoImpuestosP is not None:
        totalImpuestosP=sumaCargoImpuestosP-sumaAbonoImpuestosP
    else:
        print("Uno o ambos valores son None.")
    

    #SUMAS DE Hipotecas
    sumaAbonoH = mysql.connection.cursor()
    sumaAbonoH.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=32',[idFormato])
    resultadoH = sumaAbonoH.fetchone()
    sumaAbonoH=mysql.connection.cursor()

    if resultadoH is not None:#Comprueba si viene vacio
        sumaAbonoHipotecas= resultadoH[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalHipotecas=0
    sumaCargoH = mysql.connection.cursor()
    sumaCargoH.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=32',[idFormato])
    resultadoH = sumaCargoH.fetchone()
    sumaCargoH=mysql.connection.cursor()
    if resultadoH is not None:
        sumaCargoHipotecas = resultadoH[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoHipotecas is not None and sumaCargoHipotecas is not None:
        totalHipotecas=sumaCargoHipotecas-sumaAbonoHipotecas
    else:
        print("Uno o ambos valores son None.")

    #SUMAS DE DocumentosPL
    sumaAbonoDPL = mysql.connection.cursor()
    sumaAbonoDPL.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=33',[idFormato])
    resultadoDPL = sumaAbonoDPL.fetchone()
    sumaAbonoDPL=mysql.connection.cursor()

    if resultadoDPL is not None:#Comprueba si viene vacio
        sumaAbonoDocumentosPL= resultadoDPL[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalDocumentosPL=0
    sumaCargoDPL = mysql.connection.cursor()
    sumaCargoDPL.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=33',[idFormato])
    resultadoDPL = sumaCargoDPL.fetchone()
    sumaCargoDPL=mysql.connection.cursor()
    if resultadoDPL is not None:
        sumaCargoDocumentosPL = resultadoDPL[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoDocumentosPL is not None and sumaCargoDocumentosPL is not None:
        totalDocumentosPL=sumaCargoDocumentosPL-sumaAbonoDocumentosPL
    else:
        print("Uno o ambos valores son None.")
    

    #SUMAS DE CuentasPL
    sumaAbonoC = mysql.connection.cursor()
    sumaAbonoC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=34',[idFormato])
    resultadoC = sumaAbonoC.fetchone()
    sumaAbonoC=mysql.connection.cursor()

    if resultadoC is not None:#Comprueba si viene vacio
        sumaAbonoCuentasPL= resultadoC[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalCuentasPL=0
    sumaCargoC = mysql.connection.cursor()
    sumaCargoC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=34',[idFormato])
    resultadoC = sumaCargoC.fetchone()
    sumaCargoC=mysql.connection.cursor()
    if resultadoC is not None:
        sumaCargoCuentasPL = resultadoC[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoCuentasPL is not None and sumaCargoCuentasPL is not None:
        totalCuentasPL=sumaCargoCuentasPL-sumaAbonoCuentasPL
    else:
        print("Uno o ambos valores son None.")

    #SUMAS DE RentasC
    sumaAbonoRC = mysql.connection.cursor()
    sumaAbonoRC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=35',[idFormato])
    resultadoRC = sumaAbonoRC.fetchone()
    sumaAbonoRC=mysql.connection.cursor()

    if resultadoRC is not None:#Comprueba si viene vacio
        sumaAbonoRentasC= resultadoRC[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalRentasC=0
    sumaCargoRC = mysql.connection.cursor()
    sumaCargoRC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=35',[idFormato])
    resultadoRC = sumaCargoRC.fetchone()
    sumaCargoRC=mysql.connection.cursor()
    if resultadoRC is not None:
        sumaCargoRentasC = resultadoRC[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoRentasC is not None and sumaCargoRentasC is not None:
        totalRentasC=sumaCargoRentasC-sumaAbonoRentasC
    else:
        print("Uno o ambos valores son None.")

    #SUMAS DE InteresesC
    sumaAbonoIC = mysql.connection.cursor()
    sumaAbonoIC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=36',[idFormato])
    resultadoIC = sumaAbonoIC.fetchone()
    sumaAbonoIC=mysql.connection.cursor()

    if resultadoIC is not None:#Comprueba si viene vacio
        sumaAbonoInteresesC= resultadoIC[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalInteresesC=0
    sumaCargoIC = mysql.connection.cursor()
    sumaCargoIC.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=36',[idFormato])
    resultadoIC = sumaCargoIC.fetchone()
    sumaCargoIC=mysql.connection.cursor()
    if resultadoIC is not None:
        sumaCargoInteresesC = resultadoIC[0]
    else:
        print("No se encontraron resultados.") 
    if sumaAbonoInteresesC is not None and sumaCargoInteresesC is not None:
        totalInteresesC=sumaCargoInteresesC-sumaAbonoInteresesC
    else:
        print("Uno o ambos valores son None.")

    return render_template('vwEsquemaT.html',
                           conjuntoDatos=conjuntoDatos, 
                           consulta=consulta,
                           idFormato= idFormato,

                           sumaAbonoBanco=sumaAbonoBanco,
                           sumaCargoBanco=sumaCargoBanco,
                           totalBancos=totalBancos,

                           sumaAbonoInversiones=sumaAbonoInversiones,
                           sumaCargoInversiones=sumaCargoInversiones,
                           totalInversiones=totalInversiones,

                           sumaAbonoCajas=sumaAbonoCajas,
                           sumaCargoCajas=sumaCargoCajas,
                           totalCajas=totalCajas,
                           
                           sumaAbonoAlmacenes =sumaAbonoAlmacenes ,
                           sumaCargoAlmacenes =sumaCargoAlmacenes ,
                           totalAlmacenes =totalAlmacenes ,
                           
                           sumaAbonoClientes =sumaAbonoClientes ,
                           sumaCargoClientes =sumaCargoClientes ,
                           totalClientes =totalClientes ,

                           sumaAbonoDocumentosC =sumaAbonoDocumentosC ,
                           sumaCargoDocumentosC =sumaCargoDocumentosC ,
                           totalDocumentosC =totalDocumentosC ,

                           sumaAbonoDeudoresD =sumaAbonoDeudoresD ,
                           sumaCargoDeudoresD =sumaCargoDeudoresD ,
                           totalDeudoresD =totalDeudoresD ,

                           sumaAbonoAnticipoP =sumaAbonoAnticipoP ,
                           sumaCargoAnticipoP =sumaCargoAnticipoP ,
                           totalAnticipoP =totalAnticipoP ,

                           sumaAbonoTerreno =sumaAbonoTerreno ,
                           sumaCargoTerreno =sumaCargoTerreno ,
                           totalTerreno =totalTerreno ,

                           sumaAbonoEdificios =sumaAbonoEdificios ,
                           sumaCargoEdificios =sumaCargoEdificios ,
                           total=totalEdificios ,

                           sumaAbonoMobiliarios=sumaAbonoMobiliarios,
                           sumaCargoMobiliarios=sumaCargoMobiliarios,
                           totalMobiliarios=totalMobiliarios,

                           sumaAbonoEquipoC=sumaAbonoEquipoC,
                           sumaCargoEquipoC=sumaCargoEquipoC,
                           totalEquipoC=totalEquipoC,

                           sumaAbonoEquipoE=sumaAbonoEquipoE,
                           sumaCargoEquipoE=sumaCargoEquipoE,
                           totalEquipoE=totalEquipoE,

                           sumaAbonoDepositoG=sumaAbonoDepositoG,
                           sumaCargoDepositoG=sumaCargoDepositoG,
                           totalDepositoG=totalDepositoG,

                           sumaAbonoInversionP=sumaAbonoInversionP,
                           sumaCargoInversionP=sumaCargoInversionP,
                           totalInversionP=totalInversionP,

                           sumaAbonoGastosI=sumaAbonoGastosI,
                           sumaCargoGastosI=sumaCargoGastosI,
                           totalGastosI=totalGastosI,

                           sumaAbonoGastosE=sumaAbonoGastosE,
                           sumaCargoGastosE=sumaCargoGastosE,
                           totalGastosE=totalGastosE,

                           sumaAbonoGastosM=sumaAbonoGastosM,
                           sumaCargoGastosM=sumaCargoGastosM,
                           totalGastosM=totalGastosM,

                           sumaAbonoGastosO=sumaAbonoGastosO,
                           sumaCargoGastosO=sumaCargoGastosO,
                           totalGastosO=totalGastosO,

                           sumaAbonoGastosIn=sumaAbonoGastosIn,
                           sumaCargoGastosIn=sumaCargoGastosIn,
                           totalGastosIn=totalGastosIn,

                           sumaAbonoPapeleria=sumaAbonoPapeleria,
                           sumaCargoPapeleria=sumaCargoPapeleria,
                           totalPapeleria=totalPapeleria,

                           sumaAbonoPropaganda=sumaAbonoPropaganda,
                           sumaCargoPropaganda=sumaCargoPropaganda,
                           totalPropaganda=totalPropaganda,

                           sumaAbonoPrimasS=sumaAbonoPrimasS,
                           sumaCargoPrimasS=sumaCargoPrimasS,
                           totalPrimasS=totalPrimasS,

                           sumaAbonoRentasP=sumaAbonoRentasP,
                           sumaCargoRentasP=sumaCargoRentasP,
                           totalRentasP=totalRentasP,

                           sumaAbonoInteresesP=sumaAbonoInteresesP,
                           sumaCargoInteresesP=sumaCargoInteresesP,
                           totalInteresesP=totalInteresesP,

                           sumaAbonoProveedores =sumaAbonoProveedores ,
                           sumaCargoProveedores =sumaCargoProveedores ,
                           totalProveedores =totalProveedores ,

                           sumaAbonoDocumentosP=sumaAbonoDocumentosP,
                           sumaCargoDocumentosP=sumaCargoDocumentosP,
                           totalDocumentosP=totalDocumentosP,

                           sumaAbonoAcreedoresD=sumaAbonoAcreedoresD,
                           sumaCargoAcreedoresD=sumaCargoAcreedoresD,
                           totalAcreedoresD=totalAcreedoresD,

                           sumaAbonoAnticipoC=sumaAbonoAnticipoC,
                           sumaCargoAnticipoC=sumaCargoAnticipoC,
                           totalAnticipoC=totalAnticipoC,

                           sumaAbonoGastosP=sumaAbonoGastosP,
                           sumaCargoGastosP=sumaCargoGastosP,
                           totalGastosP=totalGastosP,

                            sumaAbonoImpuestosP=sumaAbonoImpuestosP,
                           sumaCargoImpuestosP=sumaCargoImpuestosP,
                           totalImpuestosP=totalImpuestosP,

                           sumaAbonoHipotecas=sumaAbonoHipotecas,
                           sumaCargoHipotecas=sumaCargoHipotecas,
                           totalHipotecas=totalHipotecas,

                           sumaAbonoDocumentosPL=sumaAbonoDocumentosPL,
                           sumaCargoDocumentosPL=sumaCargoDocumentosPL,
                           totalDocumentosPL=totalDocumentosPL,

                            sumaAbonoCuentasPL=sumaAbonoCuentasPL,
                           sumaCargoCuentasPL=sumaCargoCuentasPL,
                           totalCuentasPL=totalCuentasPL,

                           sumaAbonoRentasC=sumaAbonoRentasC,
                           sumaCargoRentasC=sumaCargoRentasC,
                           totalRentasC=totalRentasC,

                           sumaAbonoInteresesC=sumaAbonoInteresesC,
                           sumaCargoInteresesC=sumaCargoInteresesC,
                           totalInteresesC=totalInteresesC

                           )

@app.route('/vw_insertEsquema/<idFormato>',methods=['POST'])
def vwInsertEsquema(idFormato):
    if request.method == ('POST'):
        
        totalCajas = request.form['totalCajas1']
        totalBancos = request.form['totalBancos']
        totalInversiones = request.form['totalInversiones']
        
        totalAlmacenes = request.form['totalAlmacenes']
        totalClientes = request.form['totalClientes']
        totalDocumentosC = request.form['totalDocumentosC']
        
        totalDeudoresD = request.form['totalDeudoresD']
        totalAnticipoP = request.form['totalAnticipoP']
        totalTerreno = request.form['totalTerreno']
        totalEdificios = request.form['totalEdificios']

        totalMobiliarios = request.form['totalMobiliarios']
        totalEquipoC = request.form['totalEquipoC']
        totalEquipoE = request.form['totalEquipoE']

        totalDepositoG = request.form['totalDepositoG']
        totalInversionP = request.form['totalInversionP']
        totalGastosI = request.form['totalGastosI']
        
        totalGastosE = request.form['totalGastosE']
        totalGastosM = request.form['totalGastosM']
        totalGastosO = request.form['totalGastosO']
        totalGastosIn = request.form['totalGastosIn']
        
        totalPapeleria = request.form['totalPapeleria']
        totalPropaganda = request.form['totalPropaganda']
        totalPrimasS = request.form['totalPrimasS']

        totalRentasP = request.form['totalRentasP']
        totalInteresesP = request.form['totalInteresesP']
        totalProveedores = request.form['totalProveedores']

        totalDocumentosP = request.form['totalDocumentosP']
        totalAcreedoresD = request.form['totalAcreedoresD']
        totalAnticipoC = request.form['totalAnticipoC']
        totalGastosP = request.form['totalGastosP']
        
        totalImpuestosP = request.form['totalImpuestosP']
        totalHipotecas = request.form['totalHipotecas']
        totalDocumentosPL = request.form['totalDocumentosPL']
        
        totalCuentasPL = request.form['totalCuentasPL']
        totalRentasC = request.form['totalRentasC']
        totalInteresesC = request.form['totalInteresesC']

        if totalCajas != 0 or totalBancos != 0 or totalInversiones != 0 or totalAlmacenes != 0 or totalClientes != 0 or totalDocumentosC or totalDeudoresD != 0 or totalAnticipoP != 0 or totalTerreno != 0 or totalEdificios != 0 or totalMobiliarios !=0 or totalEquipoC != 0 or totalEquipoE != 0 or totalDepositoG != 0 or totalInversionP !=0 or totalGastosI != 0 or totalGastosE != 0 or totalGastosM !=0 or totalGastosO != 0 or totalGastosIn != 0 or totalPapeleria != 0 or totalPropaganda != 0 or totalPrimasS != 0 or totalRentasP != 0 or totalInteresesP != 0 or totalProveedores != 0 or totalDocumentosP != 0 or totalAcreedoresD != 0 or totalAnticipoC != 0 or totalGastosP != 0 or totalImpuestosP != 0 or totalHipotecas != 0 or totalDocumentosPL != 0 or totalCuentasPL != 0 or totalRentasC != 0 or totalInteresesC != 0:
            cur1=mysql.connection.cursor()
            cur1.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalCajas,1,idFormato])
            mysql.connection.commit()

            cur2=mysql.connection.cursor()
            cur2.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalBancos,2,idFormato])
            mysql.connection.commit()
        
            cur3=mysql.connection.cursor()
            cur3.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalInversiones,3,idFormato])
            mysql.connection.commit()

            cur4=mysql.connection.cursor()
            cur4.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalAlmacenes,4,idFormato])
            mysql.connection.commit()
        
            cur5=mysql.connection.cursor()
            cur5.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalClientes,5,idFormato])
            mysql.connection.commit()
        
            cur6=mysql.connection.cursor()
            cur6.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalDocumentosC,6,idFormato])
            mysql.connection.commit()

            cur7=mysql.connection.cursor()
            cur7.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalDeudoresD,7,idFormato])
            mysql.connection.commit()
        
            cur8=mysql.connection.cursor()
            cur8.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalAnticipoP,8,idFormato])
            mysql.connection.commit()
        
            cur9=mysql.connection.cursor()
            cur9.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalTerreno,9,idFormato])
            mysql.connection.commit()
        
            cur10=mysql.connection.cursor()
            cur10.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalEdificios,10,idFormato])
            mysql.connection.commit()
        
            cur11=mysql.connection.cursor()
            cur11.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalMobiliarios,11,idFormato])
            mysql.connection.commit()

            cur12=mysql.connection.cursor()
            cur12.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalEquipoC,12,idFormato])
            mysql.connection.commit()
      
            cur13=mysql.connection.cursor()
            cur13.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalEquipoE,13,idFormato])
            mysql.connection.commit()
        
            cur14=mysql.connection.cursor()
            cur14.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalDepositoG,14,idFormato])
            mysql.connection.commit()
        
            cur15=mysql.connection.cursor()
            cur15.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalInversionP,15,idFormato])
            mysql.connection.commit()
        
            cur16=mysql.connection.cursor()
            cur16.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalGastosI,16,idFormato])
            mysql.connection.commit()
        
            cur17=mysql.connection.cursor()
            cur17.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalGastosE,17,idFormato])
            mysql.connection.commit()
        
            cur18=mysql.connection.cursor()
            cur18.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalGastosM,18,idFormato])
            mysql.connection.commit()
        
            cur19=mysql.connection.cursor()
            cur19.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalGastosO,19,idFormato])
            mysql.connection.commit()
        
            cur20=mysql.connection.cursor()
            cur20.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalGastosIn,20,idFormato])
            mysql.connection.commit()
            
            cur21=mysql.connection.cursor()
            cur21.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalPapeleria,21,idFormato])
            mysql.connection.commit()
        
            cur22=mysql.connection.cursor()
            cur22.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalPropaganda,22,idFormato])
            mysql.connection.commit()
        
            cur23=mysql.connection.cursor()
            cur23.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalPrimasS,23,idFormato])
            mysql.connection.commit()
        
            cur24=mysql.connection.cursor()
            cur24.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalRentasP,24,idFormato])
            mysql.connection.commit()
        
            cur25=mysql.connection.cursor()
            cur25.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalInteresesP,25,idFormato])
            mysql.connection.commit()
        
            cur26=mysql.connection.cursor()
            cur26.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalProveedores,26,idFormato])
            mysql.connection.commit()
        
            cur27=mysql.connection.cursor()
            cur27.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalDocumentosP,27,idFormato])
            mysql.connection.commit()
        
            cur28=mysql.connection.cursor()
            cur28.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalAcreedoresD,28,idFormato])
            mysql.connection.commit()
        
            cur29=mysql.connection.cursor()
            cur29.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalAnticipoC,29,idFormato])
            mysql.connection.commit()
        
            cur30=mysql.connection.cursor()
            cur30.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalGastosP,30,idFormato])
            mysql.connection.commit()

            cur31=mysql.connection.cursor()
            cur31.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalImpuestosP,31,idFormato])
            mysql.connection.commit()

            cur32=mysql.connection.cursor()
            cur32.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalHipotecas,32,idFormato])
            mysql.connection.commit()
        
            cur33=mysql.connection.cursor()
            cur33.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalDocumentosPL,33,idFormato])
            mysql.connection.commit()
        
            cur34=mysql.connection.cursor()
            cur34.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalCuentasPL,34,idFormato])
            mysql.connection.commit()
        
            cur35=mysql.connection.cursor()
            cur35.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalRentasC,35,idFormato])
            mysql.connection.commit()
        
            cur36=mysql.connection.cursor()
            cur36.execute('INSERT INTO totales(total,concepto_id2,formato_id2) values(%s,%s,%s)',[totalInteresesC,36,idFormato])
            mysql.connection.commit()

        return redirect(url_for('vwSelectBalance',idFormato=idFormato)) 

@app.route('/vw_SelectBalance/<idFormato>')
def vwSelectBalance(idFormato):
    cur=mysql.connection.cursor()
    cur.execute('SELECT totales.total, conceptos.tipoConcepto, pasivoactivos.descripcion, totales.formato_id2 FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 1 AND totales.formato_id2 LIKE %s',[idFormato])
    consulta = cur.fetchall()

    sumaAbonoAC = mysql.connection.cursor()
    sumaAbonoAC.execute('SELECT SUM(totales.total) FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 1 AND totales.formato_id2 LIKE %s',[idFormato])
    resultadoAC = sumaAbonoAC.fetchone()

    cur1=mysql.connection.cursor()
    cur1.execute('SELECT totales.total, conceptos.tipoConcepto, pasivoactivos.descripcion, totales.formato_id2 FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 2 AND totales.formato_id2 LIKE %s',[idFormato])
    consulta1 = cur1.fetchall()

    sumaAbonoAF = mysql.connection.cursor()
    sumaAbonoAF.execute('SELECT SUM(totales.total) FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 2 AND totales.formato_id2 LIKE %s',[idFormato])
    resultadoAF = sumaAbonoAF.fetchone()
    

    cur2=mysql.connection.cursor()
    cur2.execute('SELECT totales.total, conceptos.tipoConcepto, pasivoactivos.descripcion, totales.formato_id2 FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 3 AND totales.formato_id2 LIKE %s',[idFormato])
    consulta2 = cur2.fetchall()

    sumaAbonoAD = mysql.connection.cursor()
    sumaAbonoAD.execute('SELECT SUM(totales.total) FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 3 AND totales.formato_id2 LIKE %s',[idFormato])
    resultadoAD = sumaAbonoAD.fetchone()

    sumaAF= resultadoAF[0]
    sumaAC= resultadoAC[0]
    sumaAD= resultadoAD[0]

    resultadoA = sumaAF + sumaAC + sumaAD

    cur3=mysql.connection.cursor()
    cur3.execute('SELECT totales.total, conceptos.tipoConcepto, pasivoactivos.descripcion, totales.formato_id2 FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 4 AND totales.formato_id2 LIKE %s',[idFormato])
    consulta3 = cur3.fetchall()

    sumaAbonoPC = mysql.connection.cursor()
    sumaAbonoPC.execute('SELECT SUM(totales.total) FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 4 AND totales.formato_id2 LIKE %s',[idFormato])
    resultadoPC = sumaAbonoPC.fetchone()

    cur4=mysql.connection.cursor()
    cur4.execute('SELECT totales.total, conceptos.tipoConcepto, pasivoactivos.descripcion, totales.formato_id2 FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 5 AND totales.formato_id2 LIKE %s',[idFormato])
    consulta4 = cur4.fetchall()

    sumaAbonoPF = mysql.connection.cursor()
    sumaAbonoPF.execute('SELECT SUM(totales.total) FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 5 AND totales.formato_id2 LIKE %s',[idFormato])
    resultadoPF = sumaAbonoPF.fetchone()

    cur5=mysql.connection.cursor()
    cur5.execute('SELECT totales.total, conceptos.tipoConcepto, pasivoactivos.descripcion, totales.formato_id2 FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 6 AND totales.formato_id2 LIKE %s',[idFormato])
    consulta5 = cur5.fetchall()

    sumaAbonoPD = mysql.connection.cursor()
    sumaAbonoPD.execute('SELECT SUM(totales.total) FROM totales JOIN conceptos ON totales.concepto_id2 = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 6 AND totales.formato_id2 LIKE %s',[idFormato])
    resultadoPD = sumaAbonoPD.fetchone()

    sumaPF= resultadoPF[0]
    sumaPC= resultadoPC[0]
    sumaPD= resultadoPD[0]
    resultadoP = sumaPF + sumaPC + sumaPD

    cur7=mysql.connection.cursor()
    cur7.execute('SELECT datos.monto, conceptos.tipoConcepto FROM datos JOIN conceptos ON datos.concepto_id = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 7 AND datos.formato_id LIKE %s',[idFormato])
    consulta7 = cur7.fetchall()

    capital = mysql.connection.cursor()
    capital.execute('SELECT SUM(datos.monto) FROM datos JOIN conceptos ON datos.concepto_id = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo= 7 AND datos.formato_id LIKE %s',[idFormato])
    resultadoC= capital.fetchone()
    sumaC = resultadoC [0]

    venta = mysql.connection.cursor()
    venta.execute('SELECT SUM(datos.monto) FROM datos JOIN conceptos ON datos.concepto_id = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo = 8 AND conceptos.id_concepto = 37 AND datos.formato_id = %s',[idFormato])
    resultadoV= venta.fetchone()

    CostoV = mysql.connection.cursor()
    CostoV.execute('SELECT SUM(datos.monto) FROM datos JOIN conceptos ON datos.concepto_id = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo = 8 AND conceptos.id_concepto = 38 AND datos.formato_id = %s',[idFormato])
    resultadoCV= CostoV.fetchone()

    sumaCV= resultadoCV[0]
    sumaV= resultadoV[0]

    resultadoUB= sumaV - sumaCV 

    GastosO = mysql.connection.cursor()
    GastosO.execute('SELECT SUM(datos.monto) FROM datos JOIN conceptos ON datos.concepto_id = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo = 8 AND conceptos.id_concepto = 40 AND datos.formato_id = %s',[idFormato])
    resultadoGO= GastosO.fetchone()

    sumaGO= resultadoGO[0]

    resultadoUE = resultadoUB - sumaGO    
    resultadoCS = sumaC + resultadoUE

    resultadoPasiCapi = resultadoP + resultadoCS

    cur8=mysql.connection.cursor()
    cur8.execute('SELECT datos.monto, conceptos.tipoConcepto FROM datos JOIN conceptos ON datos.concepto_id = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo = 8 AND conceptos.id_concepto = 37 AND datos.formato_id = %s',[idFormato])
    consulta8 = cur8.fetchall()

    cur9=mysql.connection.cursor()
    cur9.execute('SELECT datos.monto, conceptos.tipoConcepto FROM datos JOIN conceptos ON datos.concepto_id = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo = 8 AND conceptos.id_concepto = 38 AND datos.formato_id = %s',[idFormato])
    consulta9 = cur9.fetchall()

    cur10=mysql.connection.cursor()
    cur10.execute('SELECT datos.monto, conceptos.tipoConcepto FROM datos JOIN conceptos ON datos.concepto_id = conceptos.id_concepto JOIN pasivoactivos ON conceptos.pasivoActivo_id = pasivoactivos.id_pasivoActivo WHERE pasivoactivos.id_pasivoActivo = 8 AND conceptos.id_concepto = 40 AND datos.formato_id = %s',[idFormato])
    consulta10 = cur10.fetchall()

    cur6=mysql.connection.cursor()
    cur6.execute('SELECT * FROM formatos WHERE id_formato= %s',[idFormato])
    consulta6 = cur6.fetchall()

    
    
    return render_template('vwInsertBalance.html',
                           resultadoCS= resultadoCS, resultadoPasiCapi = resultadoPasiCapi,
                           resultadoUB = resultadoUB, resultadoUE= resultadoUE,
                           resultadoA= resultadoA,resultadoP=resultadoP, 
                           resultadoAC= resultadoAC, resultadoAF= resultadoAF ,resultadoAD= resultadoAD,
                           resultadoPC= resultadoPC, resultadoPF= resultadoPF ,resultadoPD= resultadoPD,
                           consulta7=consulta7, consulta8=consulta8,
                            consulta=consulta,consulta6=consulta6,
                            consulta1=consulta1,consulta3=consulta3, 
                            consulta4=consulta4, consulta5=consulta5,
                            consulta2=consulta2,consulta10= consulta10, 
                            consulta9 = consulta9, idFormato=idFormato)

@app.route('/vw_myBalance')
def vwMyBalance():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formatos')
    formato = cur.fetchall()
    
    return render_template('vwMyBalance.html',formato= formato)

@app.route('/vw_BalanceComprobacion/<idFormato>')
def vwBalanceComprobacion(idFormato):
    dataEsquemasT=mysql.connection.cursor()
    dataEsquemasT.execute('SELECT datos.id_dato, datos.monto, datos.deberHaber_id, conceptos.id_Concepto FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s',[idFormato])
    mysql.connection.commit()
    conjuntoDatos = dataEsquemasT.fetchall()

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formatos WHERE id_formato= %s',[idFormato])
    consulta = cur.fetchone()
    cur=mysql.connection.cursor()

    

    #SUMAS DE BANCOS
    

    sumaAbonoBa = mysql.connection.cursor()
    sumaAbonoBa.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=2',[idFormato])
    resultado = sumaAbonoBa.fetchone()
    sumaAbonoBa=mysql.connection.cursor()

    if resultado is not None:#Comprueba si viene vacio
        sumaAbonoBanco = resultado[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")

    sumaCargoBa = mysql.connection.cursor()
    sumaCargoBa.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=2',[idFormato])
    resultado = sumaCargoBa.fetchone()
    sumaCargoBa=mysql.connection.cursor()

    if resultado is not None:
        sumaCargoBanco = resultado[0]
    else:
        print("No se encontraron resultados.") 

    totalBancos1 = 0
    totalBancos = 0  # Valor predeterminado

    # ... Código para calcular sumaAbonoBanco y sumaCargoBanco ...

    if sumaAbonoBanco is not None and sumaCargoBanco is not None:
        if sumaAbonoBanco >= sumaCargoBanco:
            totalBancos = sumaAbonoBanco - sumaCargoBanco
        else:
            totalBancos1 = sumaCargoBanco - sumaAbonoBanco

    elif sumaAbonoBanco is None and sumaCargoBanco is None:
        print("Ambos valores son None.")
    else:
        print("Uno de los valores es None.")

         #SUMAS DE CAJA
    sumaAbonoCa = mysql.connection.cursor()
    sumaAbonoCa.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=1',[idFormato])
    resultadoCa = sumaAbonoCa.fetchone()
    sumaAbonoCa=mysql.connection.cursor()

    totalCajas=0
    totalCajas1=0

    if resultadoCa is not None:#Comprueba si viene vacio
        sumaAbonoCajas= resultadoCa[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")

    sumaCargoCa = mysql.connection.cursor()
    sumaCargoCa.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=1',[idFormato])
    resultadoCa = sumaCargoCa.fetchone()
    sumaCargoCa=mysql.connection.cursor()
    
    if resultadoCa is not None:
        sumaCargoCajas = resultadoCa[0]
    else:
        print("No se encontraron resultados.")
    

    # ... Código para calcular sumaAbonoBanco y sumaCargoBanco ...

    if sumaAbonoCajas is not None and sumaCargoCajas is not None:
        if sumaAbonoCajas >= sumaCargoCajas:
            totalCajas = sumaAbonoCajas - sumaCargoCajas
        else:
            totalCajas1 = sumaCargoCajas - sumaAbonoCajas

    elif sumaAbonoCajas is None and sumaCargoCajas is None:
        print("Ambos valores son None.")
    else:
        print("Uno de los valores es None.")

     #SUMAS DE Inversiones
    sumaAbonoIn = mysql.connection.cursor()
    sumaAbonoIn.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=1 AND datos.concepto_id=3',[idFormato])
    resultadoIn = sumaAbonoIn.fetchone()
    sumaAbonoIn=mysql.connection.cursor()

    if resultadoIn is not None:#Comprueba si viene vacio
        sumaAbonoInversiones = resultadoIn[0]  # Acceder al valor de la suma
    else:
        print("No se encontraron resultados.")
    totalInversiones=0
    totalInversiones1=0

    sumaCargoIn = mysql.connection.cursor()
    sumaCargoIn.execute('SELECT SUM(datos.monto) FROM formatos INNER JOIN datos ON formatos.id_formato = datos.formato_id INNER JOIN conceptos ON datos.concepto_id=conceptos.id_concepto WHERE formatos.id_formato=%s AND datos.deberHaber_id=2 AND datos.concepto_id=3',[idFormato])
    resultadoIn = sumaCargoIn.fetchone()
    sumaCargoIn=mysql.connection.cursor()

    if resultadoIn is not None:
        sumaCargoInversiones = resultadoIn[0]
    else:
        print("No se encontraron resultados.")

    if sumaAbonoInversiones is not None and sumaCargoInversiones is not None:
        if sumaAbonoCajas >= sumaCargoInversiones:
            totalInversiones = sumaAbonoInversiones - sumaCargoInversiones
        else:
            totalInversiones1 = sumaCargoInversiones - sumaAbonoInversiones

    elif sumaAbonoInversiones is None and sumaCargoInversiones is None:
        print("Ambos valores son None.")
    else:
        print("Uno de los valores es None.")

    
   

    


    
    return render_template('vwBalanceComprobacion.html',
                           conjuntoDatos=conjuntoDatos, 
                           consulta=consulta,
                           idFormato= idFormato,

                           sumaAbonoBanco=sumaAbonoBanco,
                           sumaCargoBanco=sumaCargoBanco,
                           totalBancos=totalBancos,
                           totalBancos1=totalBancos1,
                        

                           sumaAbonoCajas=sumaAbonoCajas,
                           sumaCargoCajas=sumaCargoCajas,
                           totalCajas=totalCajas,
                           totalCajas1=totalCajas1,

                           sumaAbonoInversiones=sumaAbonoInversiones,
                           sumaCargoInversiones=sumaCargoInversiones,
                           totalInversiones=totalInversiones,
                            totalInversiones1=totalInversiones1,

                        
    
                           )



if __name__ == '__main__':
    app.add_url_rule('/',view_func=index)
    app.run(debug=True, port=5005)
