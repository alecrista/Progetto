# DATABASE MOTOMONDIALE 2005-2017
Con questo progetto andremo ad analizzare il meglio (e il peggio) del Motomondiale nel periodo 2005-2017. Il database originale lo si può trovare sulla seguente piattaforma:  
[**Database originale**](https://raw.githubusercontent.com/nbugliar/motogp_regression/master/MotoGP_2005_2017.csv)  
Le operazioni eseguite, messe insieme, non saranno altro che un'analisi esplorativa, un pochino particolare forse, sui dati di cui dispone il database.  
Trattandosi di competizioni le principali misure che verranno prese saranno punteggie e velocità, ma ci saranno anche altri dati curiosi da analizzare.  
### Piccoli problemi inziali
Il database originale non è perfetto: ho dovuto inizialmente rimuovere i dati inutili, come ad esempio, in caso di gare interrotte dalla bandiera rossa con successiva ripartenza, le classifiche delle gare al momento dell'interruzione. Ai fini della nostra analisi esse sarebbero state inutili, pocihé la classifica finale, in quei casi appunto di ripartenza, è data dall'arrivo della _"seconda"_ gara.  
Poi ho dovuto aggiungere punteggi mancanti a certi Gran Premi (ad esempio il GP di Repubblica Ceca 2005 classe MotoGP), per motivi ignoti e poi sostituire eventuali doppioni sia tra le case costruttrici che tra i piloti (es. nel database il pilota Dani PEDROSA appariva sia con il nome "Dani PEDROSA " che con il nome "Daniel PEDROSA", quindi il programma lo avrebbe considerato come 2 piloti diversi). Per farlo ho usato il comando:  
```
data=data.with_columns(
    pl.col("Rider_Name").str.replace("Daniel PEDROSA","Dani PEDROSA").alias("Rider_Name"),
    pl.col("Bike").str.replace("Yamaha Forward","Forward Yamaha").alias("Bike")
)
```
Sì, perché ho avuto lo stesso problema con la casa costruttrica Forward Yamaha.
## Introduzione
Per iniziare era necessario che un utente, passandomi il termine, "ignorante" in questo campo ottenesse giusto un'infarinatura su chi, a livello di successo puro, tra costruttori e piloti, fosse effettivamente stato il migliore, cosicchè ci si trovasse molto meno spaesati di fronte a moli così elevate di dati di cui magari non si conosce niente.
## Classifiche generali
In questa prima sezione l'utente ottiene un'ulteriore infarinatura su ciò che analizzerà, attraverso l'osservazione delle classifiche piloti e costruttori di ciascuna categoria per ciascuna annata.  
Da notare che la classifica della classe 125cc del 2005 è alterata rispetto alla realtà **a causa dell'assenza**, nel dataset, **dei risultati del GP di Spagna 2005 della categoria stessa.**  
A parte questo tutte le altre classfiche non dovrebbero presentare problemi. Ulteriori descrizioni sono presenti nell'interfaccia del progetto.
## Risultati di ogni GP per categoria
Essendo il database un insieme dei risultati di ogni gara, mi è sembrato giusto sfruttare questa caratteristica per poter rappresentare le classifiche di un gp a scelta dell'utente, un po' come si può fare sul [sito ufficiale della Motogp.](https://www.motogp.com/en/gp-results/2017/val/motogp/rac/classification)  
Come si può notare tra i risultati sono assenti i ritiri. Questo perché nel contesto dell'analisi che un pilota si ritiri, non corra una gara o e fuori per infortunio comunque egli totalizza zero punti, cosa che all'utente medio, proabilmente, interessa molto molto meno. Ho deciso di conseguenza, anche per difficoltà di programmazione nel farlo, **di non inserirli.**
### Chicca
Come si può vedere, inoltre, ho deciso, siccome in possessione anche delle date di ogni singolo GP nel database, di sfruttare queste informazioni per usare la funzione di Streamlit che permette di giochicchiare con le date.  
Infatti ho inserito 2 modalità di selezione: **_Gran Premio - Anno_**, dove l'utente inserisce prima un'annnata a scelta e poi uno o più GP di quella annata per scoprirne i risultati per ogni categoria, oppure **_Per data_**, dove l'utente può selezionare una data a sua scelta e vedere, in caso di GP corso in quella data, i risultati di quel GP.
Ecco il codice usato:
```
mod=st.selectbox("Inserire modalità di filtraggio:", ["Gran Premio - Anno", "Per data"])
if mod==str("Gran Premio - Anno"):
    #Siccome voglio che la casella di selezione del gran premio sia basata sul calendario di gare e no sull'ordine alfabetico,
    #allora dovrò fare il seguente lavoro:
    year1=st.select_slider("Inserire anno:", range(2005,2018), key=2)
    dataytd=data.select("Year","TRK","Date")
    dataytd_filt=dataytd.filter(pl.col("Year")==year1).select("TRK", "Date")
    pd_ytd=pd.DataFrame(dataytd_filt)
    pd_ytd=pd_ytd.rename(columns={0:"TRK",1:"Date"})
    datasort1=pd_ytd.drop_duplicates(subset="TRK").sort_values("Date")
    trk=st.multiselect("Inserire GP:", datasort1["TRK"].to_list())
    for i in trk:
        st.write(i, year1)
        col11, col12, col13=st.columns(3)
        d1=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category")=="MotoGP").filter(pl.col("Year")==year1).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","Year", pl.col("TRK").alias("GP"), "Track").sort("Position", descending=False)
        col11.write(d1) #risultati MotoGP
        d2=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["250cc", "Moto2"])).filter(pl.col("Year")==year1).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","Year", pl.col("TRK").alias("GP"), "Track").sort("Position", descending=False)
        col12.write(d2) #risultati Moto2/250cc
        d3=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["125cc", "Moto3"])).filter(pl.col("Year")==year1).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","Year", pl.col("TRK").alias("GP"), "Track").sort("Position", descending=False)
        col13.write(d3) #risultati Moto3/125cc
elif mod==str("Per data"):
    data_amg=st.date_input("Inserire data:", min_value=dt.date(2005, 1, 1), max_value=dt.date(2017, 12, 31))
    data_date=data.with_columns(pl.col("Date").str.strptime(pl.Date, "%Y-%m-%d").alias("PyDate"))
    col11, col12, col13=st.columns(3)
    d1=data_date.filter(pl.col("PyDate")==data_amg).filter(pl.col("Category")=="MotoGP").filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points",pl.col("TRK").alias("GP"),"Track","PyDate").sort("Position", descending=False)
    col11.write(d1) #risultati MotoGP
    d2=data_date.filter(pl.col("PyDate")==data_amg).filter(pl.col("Category").is_in(["250cc", "Moto2"])).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points",pl.col("TRK").alias("GP"),"Track","PyDate").sort("Position", descending=False)
    col12.write(d2) #risultati Moto2/250cc
    d3=data_date.filter(pl.col("PyDate")==data_amg).filter(pl.col("Category").is_in(["125cc", "Moto3"])).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points",pl.col("TRK").alias("GP"),"Track","PyDate").sort("Position", descending=False)
    col13.write(d3) #risultati Moto3/125cc
```
