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
Codice completo per l'inserimento e le modifiche del caso dei dati:  
```
import streamlit as st
import altair as alt
import polars as pl
import datetime as dt
import pandas as pd
import math as mt
#git@github.com:alecrista/Progetto.git, utile per evitare di fare sempre l'accesso a Github
data=pl.read_csv("MotoGP_2005_2017.csv", null_values=[" ","NA","crash"])
st.session_state.data=data
st.title("Database Motomondiale 2005-2017")
st.header("Database completo da analizzare, disordinato:")
st.write("Nelle colonne Position e Finish_Time, dove mancano i valori, è perché il pilota non ha terminato il Gran Premio.")
st.write("__PURTROPPO, PER RAGIONI A NOI IGNOTE, NEL DATASET MANCANO I RISULTATI DEL GP DI SPAGNA CLASSE 125cc. LE CLASSIFICHE DI QUELLA STAGIONE RISULTAERANNO QUINDI ALTERATE.__")
st.write(data)
#Effettuo delle correzioni sul dataset
data_rac=data.filter(pl.col("Session")=="RAC")
data_rac2=data.filter(pl.col("Session")=="RAC2")
merged=data_rac.join(data_rac2, on=["Year","TRK","Track","Category","Date","Position","GP","track_length_km","l_corners","r_corners","width_m",
                                    "straight_m","GP_avg_speed","gp_dist","m2_dist","m3_dist"], how="left")
data=merged.with_columns([
    pl.coalesce(["Session_right","Session"]).alias("Session"),
    pl.coalesce(["Track_Condition_right","Track_Condition"]).alias("Track_Condition"),
    pl.coalesce(["Track_Temp_right","Track_Temp"]).alias("Track_Temp"),
    pl.coalesce(["Air_Temp_right","Air_Temp"]).alias("Air_Temp"),
    pl.coalesce(["Humidity_right","Humidity"]).alias("Humidity"),
    pl.coalesce(["Points_right","Points"]).alias("Points"),
    pl.coalesce(["Rider_Number_right","Rider_Number"]).alias("Rider_Number"),
    pl.coalesce(["Rider_Name_right","Rider_Name"]).alias("Rider_Name"),
    pl.coalesce(["Nationality_right","Nationality"]).alias("Nationality"),
    pl.coalesce(["Team_Name_right","Team_Name"]).alias("Team_Name"),
    pl.coalesce(["Bike_right","Bike"]).alias("Bike"),
    pl.coalesce(["Avg_Speed_right","Avg_Speed"]).alias("Avg_Speed"),
    pl.coalesce(["Time_right","Time"]).alias("Time"),
    pl.coalesce(["Finish_Time_right","Finish_Time"]).alias("Finish_Time")
])
data=data.with_columns(pl.when(pl.col("Position")==1).then(pl.lit(25)).otherwise(
    pl.when(pl.col("Position")==2).then(pl.lit(20)).otherwise(
        pl.when(pl.col("Position")==3).then(pl.lit(16)).otherwise(
            pl.when(pl.col("Position")==4).then(pl.lit(13)).otherwise(
                pl.when(pl.col("Position")==5).then(pl.lit(11)).otherwise(
                    pl.when(pl.col("Position")==6).then(pl.lit(10)).otherwise(
                        pl.when(pl.col("Position")==7).then(pl.lit(9)).otherwise(
                            pl.when(pl.col("Position")==8).then(pl.lit(8)).otherwise(
                                pl.when(pl.col("Position")==9).then(pl.lit(7)).otherwise(
                                    pl.when(pl.col("Position")==10).then(pl.lit(6)).otherwise(
                                        pl.when(pl.col("Position")==11).then(pl.lit(5)).otherwise(
                                            pl.when(pl.col("Position")==12).then(pl.lit(4)).otherwise(
                                                pl.when(pl.col("Position")==13).then(pl.lit(3)).otherwise(
                                                    pl.when(pl.col("Position")==14).then(pl.lit(2)).otherwise(
                                                        pl.when(pl.col("Position")==15).then(pl.lit(1)).otherwise(
                                                            pl.lit(0))
                                                        )
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    ).alias("Points_corr")
)
data=data.with_columns([
    pl.coalesce(["Points_corr","Points"]).alias("Points")
])
data=data.with_columns(
    pl.col("Rider_Name").str.replace("Daniel PEDROSA","Dani PEDROSA").alias("Rider_Name"),
    pl.col("Bike").str.replace("Yamaha Forward","Forward Yamaha").alias("Bike")
)
```
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
## Analisi per pilota
In questa seconda sezione viene semplicemente eseguito il primo vero insieme di operazioni di analisi esplorativa, usando i piloti come unità statistica.
### Piloti e punti conquistati
A questo punto entra in gioco, oltre agli operatori di selezione e conseguente filtraggio, anche la libreria **altair**, utile per svolgere analisi grafiche.  
Si confrontano semplicemente le annate di ciascun pilota in base ai punti conquistati da egli alla fine di ogni campionato. Ovviamente vengono fatte distinzioni anche di categorie e c'è anche la possibilità di selezioanre il periodo che più interessa, attraverso uno slider. Viene quindi raffigurata sulla sinistra la tabella con gli opportuni filtraggi eseguiti dall'utente e sulla destra un grafico a linee utile per comprendere meglio i dati che si stanno osservando.  
Questo il codice:  
```
data_rider_points=data.group_by("Rider_Name","Year","Category").agg(pl.col("Points").sum(), pl.col("Bike").implode().list.unique()).sort("Rider_Name", "Year", descending=True)
data_rider_points=data_rider_points.drop_nulls() #dataset dei punteggi di ogni pilota in ogni stagione
col111, col112=st.columns(2)
rider_list=sorted(data.select(pl.col("Rider_Name").unique()).drop_nulls().to_series().to_list()) #lista di selezione piloti
st.session_state.rider_list=rider_list #salvo la lista a session state per sicurezza
riders=col111.multiselect("Inserire piloti desiderati:", rider_list) #operatore di filtraggio per pilota
d_filt_1=data_rider_points.filter(pl.col("Rider_Name").is_in(riders)) #dataset filtrato per pilota
if len(riders)!=0:
    cat_list=sorted(d_filt_1.select(pl.col("Category").unique()).to_series().to_list()) #lista di selezione categorie
    category=col112.multiselect("Inserire categoria desiderata:", cat_list, default=cat_list) #operatore di filtraggio per categoria
    d_filt_2=d_filt_1.filter(pl.col("Category").is_in(category)) #dataset filtrato per pilota e per categorie
    if len(category)!=0:
        year_list=sorted(d_filt_2.select(pl.col("Year").unique()).to_series().to_list()) 
        year=col112.slider("Inserire periodo da analizzare:", min_value=year_list[0], max_value=max(year_list), value=(year_list[0], max(year_list))) #filtraggio per annata massima
        col111.write(d_filt_2.sort("Year", "Rider_Name", descending=True).filter(pl.col("Year")<=year[1], pl.col("Year")>=year[0]))
        col112.altair_chart(
            alt.Chart(d_filt_2.filter(pl.col("Year")<=year[1], pl.col("Year")>=year[0])).mark_line().encode(alt.X("Year"), alt.Y("Points").scale(zero=False), alt.Color("Rider_Name")),
            use_container_width=True
        ) #grafico a linee del dataset finale filtrato per annata massima
    else:
        year_list=sorted(d_filt_1.select(pl.col("Year").unique()).to_series().to_list())
        year=col112.slider("Inserire periodo da analizzare:", min_value=year_list[0], max_value=max(year_list), value=(year_list[0], max(year_list))) #filtraggio per annata massima
        col111.write(d_filt_1.sort("Year", "Rider_Name", descending=True).filter(pl.col("Year")<=year[1], pl.col("Year")>=year[0]))
        col112.altair_chart(
            alt.Chart(d_filt_1.filter(pl.col("Year")<=year[1], pl.col("Year")>=year[0])).mark_line().encode(alt.X("Year"), alt.Y("Points").scale(zero=False), alt.Color("Rider_Name")),
            use_container_width=True
        ) #grafico a linee del dataset filtrato per annata massima
else:
    cat_list=sorted(data_rider_points.select(pl.col("Category").unique()).to_series().to_list())
    category=col112.multiselect("Inserire Categoria desiderata:", cat_list, default=cat_list)
    d_filt_3=data_rider_points.filter(pl.col("Category").is_in(category))
    if len(category)!=0:
        year_list=sorted(d_filt_3.select(pl.col("Year").unique()).to_series().to_list())
        year=col112.slider("Inserire periodo da analizzare:", min_value=year_list[0], max_value=max(year_list), value=(year_list[0], max(year_list))) #filtraggio per annata massima
        col111.write(d_filt_3.sort("Year", "Rider_Name", descending=True).filter(pl.col("Year")<=year[1], pl.col("Year")>=year[0]))
        col112.altair_chart(
            alt.Chart(d_filt_3.filter(pl.col("Year")<=year[1], pl.col("Year")>=year[0])).mark_line().encode(alt.X("Year"), alt.Y("Points").scale(zero=False)),
            use_container_width=True
        )
    else:
        year_list=sorted(data_rider_points.select(pl.col("Year").unique()).to_series().to_list())
        year=col112.slider("Inserire periodo da analizzare:", min_value=year_list[0], max_value=max(year_list), value=(year_list[0], max(year_list))) #filtraggio per annata massima
        col111.write(data_rider_points.sort("Year", "Rider_Name", descending=True).filter(pl.col("Year")<=year[1], pl.col("Year")>=year[0]))
        col112.altair_chart(
            alt.Chart(data_rider_points.filter(pl.col("Year")<=year[1], pl.col("Year")>=year[0])).mark_line().encode(alt.X("Year"), alt.Y("Points").scale(zero=False), alt.Color("Rider_Name")),
            use_container_width=True
        )
```