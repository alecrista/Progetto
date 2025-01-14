# DATABASE MOTOMONDIALE 2005-2017: DESCRIZIONE
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
Codice per grafici e tabelle in output:  
```
data_wins=data.filter(pl.col("Position")==1) #dataset con tutti i vincitori di tutti i gp
data_winners=data_wins.group_by("Rider_Name").agg(pl.col("Points").count().alias("N_wins")) #dataset con il conteggio delle vittorie
win1, win2=st.columns(2)
win1.write(data_winners.sort("N_wins", descending=True))
win_chart=alt.Chart(
    data_winners.filter(pl.col("N_wins")>10)).mark_bar().encode(alt.Y("Rider_Name", sort=alt.EncodingSortField(field="N_wins", order="descending")), alt.X("N_wins"),
    alt.Color("N_wins").scale(type="log"))
win2.altair_chart(win_chart, use_container_width=True) #grafico delle vittorie
#Faccio lo stesso procedimento ma con le case motociclistiche
st.subheader("I costruttori più vincenti nel periodo in questione")
data_winners_cons=data_wins.group_by("Bike").agg(pl.col("Points").count().alias("N_wins")) #dataset con il conteggio delle vittorie
win11, win12=st.columns(2)
win11.write(data_winners_cons.sort("N_wins", descending=True))
win_cons_chart=alt.Chart(
    data_winners_cons.filter(pl.col("N_wins")>10)).mark_bar().encode(alt.Y("Bike", sort=alt.EncodingSortField(field="N_wins", order="descending")), alt.X("N_wins"),
    alt.Color("N_wins").scale(type="log"))
win12.altair_chart(win_cons_chart, use_container_width=True) #grafico delle vittorie
#ADESSO RIPETO GLI STESSI PROCEDIMENTI, MA CON I PODI
st.subheader("I piloti con più podi nel periodo in questione")
data_pod=data.filter(pl.col("Position")<=3) #dataset con tutti i podi di tutti i gp
data_podiums=data_pod.group_by("Rider_Name").agg(pl.col("Points").count().alias("N_podiums")) #dataset con il conteggio dei podi
pod1, pod2=st.columns(2)
pod1.write(data_podiums.sort("N_podiums", descending=True))
pod_chart=alt.Chart(
    data_podiums.filter(pl.col("N_podiums")>50)).mark_bar().encode(alt.Y("Rider_Name", sort=alt.EncodingSortField(field="N_podiums", order="descending")), alt.X("N_podiums"),
    alt.Color("N_podiums").scale(type="log"))
pod2.altair_chart(pod_chart, use_container_width=True) #grafico dei podi
#Faccio lo stesso procedimento ma con le case motociclistiche
st.subheader("I costruttori con più podi nel periodo in questione")
data_podiums_cons=data_pod.group_by("Bike").agg(pl.col("Points").count().alias("N_podiums")) #dataset con il conteggio delle vittorie
pod11, pod12=st.columns(2)
pod11.write(data_podiums_cons.sort("N_podiums", descending=True))
#data_winners_cons_pd=pd.DataFrame(data_winners_cons) #uso Pandas così altair può riordinare il grafico in base al numero di vittorie
pod_cons_chart=alt.Chart(
    data_podiums_cons.filter(pl.col("N_podiums")>50)).mark_bar().encode(alt.Y("Bike", sort=alt.EncodingSortField(field="N_podiums", order="descending")), alt.X("N_podiums"),
    alt.Color("N_podiums").scale(type="log"))
pod12.altair_chart(pod_cons_chart, use_container_width=True) #grafico delle vittorie
```
## Classifiche generali
In questa prima sezione l'utente ottiene un'ulteriore infarinatura su ciò che analizzerà, attraverso l'osservazione delle classifiche piloti e costruttori di ciascuna categoria per ciascuna annata.  
Da notare che la classifica della classe 125cc del 2005 è alterata rispetto alla realtà **a causa dell'assenza**, nel dataset, **dei risultati del GP di Spagna 2005 della categoria stessa.**  
A parte questo tutte le altre classfiche non dovrebbero presentare problemi. Ulteriori descrizioni sono presenti nell'interfaccia del progetto, assieme al sistema di punteggio sul quale si basano le classifiche.
Comandi per la creazione delle classifche:  
```
#col1 e col2 colonne create in precedenza
year=col1.select_slider("Inserire anno:", range(2005,2018), key=1)
if year>2011:
    cat=col2.select_slider("Inserire Categoria:", ["MotoGP","Moto2","Moto3"])
elif (year>2009 and year<=2011):
    cat=col2.select_slider("Inserire Categoria:", ["MotoGP","Moto2","125cc"])
else:
    cat=col2.select_slider("Inserire Categoria:", ["MotoGP","250cc","125cc"])
# NEL GROUP BY TUTTE LE ALTRE COLONNE VANNO PERSE, PER CUI LE COLONNE DI FILTRAGGIO VANNO INSERITE.
col1.subheader("Classifica piloti")
class_piloti=data.group_by("Year","Category","Rider_Name","Nationality").agg(
    pl.col("Points").sum(), pl.col("Bike").implode().list.unique()).filter(pl.col("Year")==year).filter(
        pl.col("Category")==cat).sort("Points", descending=True) #classifica piloti
col1.write(class_piloti)
# v---classsifica costruttori----v
col2.subheader("Classifica costruttori")
costr=data.group_by("Year", "TRK", "Category", "Bike").agg(pl.col("Points").max().alias("Tot_points")).sort("Year","Category","Bike", descending=True)
class_costr=costr.group_by("Year", "Category", "Bike").agg(pl.col("Tot_points").sum()).filter(pl.col("Year")==year, pl.col("Category")==cat).sort("Tot_points", descending=True)
col2.write(class_costr.drop_nulls())
```
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
A questo punto entra in gioco, oltre agli operatori di selezione e conseguente filtraggio, anche la libreria **altair**, utile per svolgere analisi grafiche, usata anche nell'introduzione ma non in maniera interattiva.  
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
### Piloti e velocità dura e pura
In questa sottosezione ho deciso di confrontare le velocità medie di ogni pilota in ogni annata, attraverso la variabile *_Avg_Speed_*, differenziando per condizioni della pista (asciutta o bagnata) e per categoria. Da questo punto in poi notare che la variabile *_Category_* verrà riassunta sempre nella variabile *_Cat_*, che riunisce le classi 125cc e Moto3 nella categoria Lightweight e le classi 250cc e Moto2 nella categoria Middleweight (Moto2 e Moto3 sono le sostitute con motori 4 tempi rispettivamente di 250cc e 125cc con motori a 2 tempi).
Le parti ad interazione sono state precedute da piccole pre-analisi generali di tutti i dati di velocità media differenziati per categoria e condizioni di pista.
Questo il codice usato:
```
data_rider_speed=data.group_by("Rider_Name","Year","Category","Bike","Track_Condition").agg(
    pl.col("Avg_Speed").mean()).sort("Rider_Name", "Year", descending=True).drop_nulls() #dataset con tutti i piloti e tutte le velocità medie per ogni condizione.
#
st.write("__*Pista asciutta*__")
mud=data_rider_speed.filter(pl.col("Track_Condition")=="Dry").select(pl.col("Avg_Speed").mean())[0,0]
#Quella che si creerebbe qua sopra sarebbe a tutti gli effetti una tabella, con un solo valore.
#Servendomi tuttavia solo il singolo valore lo seleziono con il comando di indicizzazione [0, 0] (riga 0, colonna 0)
st.write("Velocità media di tutti i piloti con pista asciutta:", mud)
d_dry=data_rider_speed.filter(pl.col("Track_Condition")=="Dry")
d_dry_gen=d_dry.group_by("Year","Category").agg(pl.col("Avg_Speed").mean()).sort("Year","Category", descending=False)
d_dry_gen=d_dry_gen.with_columns( #Dataset con medie complessive e variabile Category riassunta nella seguente maniera
    pl.when(pl.col("Category").is_in(["125cc","Moto3"]))
    .then(pl.lit("Lightweight"))
    .otherwise(pl.when(pl.col("Category").is_in(["250cc","Moto2"]))
               .then(pl.lit("Middleweight"))
               .otherwise(pl.lit("MotoGP")))
               .alias("Cat"))
dry1, dry2=st.columns(2)
dry1.write(d_dry_gen.sort("Year",descending=False).sort("Cat", descending=True))
chart_dry=alt.Chart(d_dry_gen).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed").scale(zero=False), alt.Color("Cat").scale(domain=['Lightweight', 'Middleweight', 'MotoGP'], range=['#FF0000', '#00FF00', '#0000FF']),
                                                  alt.Text("Avg_Speed"))
dry2.altair_chart(chart_dry, use_container_width=False)
st.write("Svolgiamo un'analisi pilota per pilota. A destra avremo la tabella con i dati cercati dall'utente, ovvero pilota, categoria e range di annate, in basso un grafico riassuntivo per ogni categoria.")
st.write("Piccola chicca: nel 2015 Joan Mir ha ottenuto con una Moto3 una velocità media comparabile a quella dei piloti di MotoGP. Questo perché quest'analisi tiene conto della media aritmetica, non ponderata."
             " Infatti Mir quella stagione corse solo nel GP di Australia che normalmente ha velocità medie molto elevate.")
dry1, dry2=st.columns(2)
d_dry_rid=d_dry.group_by("Year","Category","Rider_Name","Bike").agg(pl.col("Avg_Speed").mean()).sort("Year","Rider_Name","Category", descending=False)
d_dry_rid=d_dry_rid.with_columns( #Dataset con variabile categoria riassunta e con dati su pista asciutta
    pl.when(pl.col("Category").is_in(["125cc","Moto3"]))
    .then(pl.lit("Lightweight"))
    .otherwise(pl.when(pl.col("Category").is_in(["250cc","Moto2"]))
               .then(pl.lit("Middleweight"))
               .otherwise(pl.lit("MotoGP")))
               .alias("Cat"))
rid_dry=sorted(d_dry_rid.select("Rider_Name").unique().to_series().to_list()) 
st.session_state.rid_dry=rid_dry #"salvo" la lista di piloti attraverso session_state
rid_dry_sel=dry1.multiselect("Selezionare pilota/i desiderato/i:", rid_dry)
if len(rid_dry_sel)==0:
    st.write("Inserire almeno un pilota.")
else:
    data_dry_rid=d_dry_rid.filter(pl.col("Rider_Name").is_in(rid_dry_sel))
    year_dry=sorted(data_dry_rid.select("Year").unique().to_series().to_list())
    st.session_state.year_dry=year_dry #"salvo" la lista di annate attraverso session_state
    #Operazioni di filtraggio per anno e categoria---v
    year_dry_sel=dry1.slider("Selezionare periodo desiderato:", min_value=year_dry[0], max_value=max(year_dry), value=(year_list[0], max(year_list)))
    data_dry_rid_year=data_dry_rid.filter(pl.col("Year")>=year_dry_sel[0], pl.col("Year")<=year_dry_sel[1])
    cat_dry=sorted(data_dry_rid_year.select("Cat").unique().to_series().to_list())
    st.session_state.cat_dry=cat_dry #"salvo" la lista di categorie attraverso session_state
    cat_dry_sel=dry1.multiselect("Selezionare categoria desiderata", cat_dry, default=cat_dry)
    data_dry_rid_year_cat=data_dry_rid_year.filter(pl.col("Cat").is_in(cat_dry_sel)) #fdataset filtrato
    dry2.write(data_dry_rid_year_cat)
    st.altair_chart(alt.Chart(data_dry_rid_year_cat).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed").scale(zero=False), alt.Color("Rider_Name")),
                use_container_width=True)
### RIPETO LO STESSO IDENTICO PROCEDIMENTO ANCHE CON PISTA BAGNATA. AL POSTO DI DRY O D TROVEREMO WET O W NELLA NOMENCLATURA DEGLI OPERATORI DI FILTRAGGIO O DE DATASET
### MA ESSI SVOLGERANNO LE STESSE IDENTICHE MANSIONI DI PRIMA.
st.write("__*Pista bagnata*__")
muw=data_rider_speed.filter(pl.col("Track_Condition")=="Wet").select(pl.col("Avg_Speed").mean())[0,0]
st.write("Velocità media di tutti i piloti con pista bagnata:", muw)
d_wet=data_rider_speed.filter(pl.col("Track_Condition")=="Wet")
d_wet_gen=d_wet.group_by("Year","Category").agg(pl.col("Avg_Speed").mean()).sort("Year","Category", descending=False)
d_wet_gen=d_wet_gen.with_columns(
    pl.when(pl.col("Category").is_in(["125cc","Moto3"]))
    .then(pl.lit("Lightweight"))
    .otherwise(pl.when(pl.col("Category").is_in(["250cc","Moto2"]))
               .then(pl.lit("Middleweight"))
               .otherwise(pl.lit("MotoGP")))
               .alias("Cat"))
wet1,wet2=st.columns(2)
wet1.write(d_wet_gen.sort("Year",descending=False).sort("Cat", descending=True))
chart_wet=alt.Chart(d_wet_gen).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed").scale(zero=False), alt.Color("Cat").scale(domain=['Lightweight', 'Middleweight', 'MotoGP'], range=['#FF0000', '#00FF00', '#0000FF']),
                                                  alt.Text("Avg_Speed"))
wet2.altair_chart(chart_wet, use_container_width=False)
st.write("Da notare che curiosamente nel 2014, la classe leggera è stata più veloce in media rispetto alla classe di mezzo."
         " Questo probablimente perché ha corso meno gare con pista bagnata, con un asfalto molto meno bagnato in quelle occasioni e anche in piste mediamente più veloci.")
st.write("Svolgiamo un'analisi pilota per pilota.")
wet1, wet2=st.columns(2)
d_wet_rid=d_wet.group_by("Year","Category","Rider_Name","Bike").agg(pl.col("Avg_Speed").mean()).sort("Year","Rider_Name","Category", descending=False)
d_wet_rid=d_wet_rid.with_columns(
    pl.when(pl.col("Category").is_in(["125cc","Moto3"]))
    .then(pl.lit("Lightweight"))
    .otherwise(pl.when(pl.col("Category").is_in(["250cc","Moto2"]))
               .then(pl.lit("Middleweight"))
               .otherwise(pl.lit("MotoGP")))
               .alias("Cat"))
rid_wet=sorted(d_wet_rid.select("Rider_Name").unique().to_series().to_list())
st.session_state.rid_wet=rid_wet #"salvo" per sicurezza la lista di piloti (dataset pista bagnata)
rid_wet_sel=wet1.multiselect("Selezionare pilota desiderato", rid_wet)
if len(rid_wet_sel)==0:
    st.write("Inserire almeno un pilota")
else:
    data_wet_rid=d_wet_rid.filter(pl.col("Rider_Name").is_in(rid_wet_sel))
    year_wet=sorted(data_wet_rid.select("Year").unique().to_series().to_list())
    st.session_state.year_wet=year_wet
    year_wet_sel=wet1.slider("Selezionare periodo da analizzare:", min_value=year_wet[0], max_value=max(year_wet), value=(year_wet[0],max(year_wet)), key=3)
    data_wet_rid_year=data_wet_rid.filter(pl.col("Year")<=year_wet_sel[1], pl.col("Year")>=year_wet_sel[0])
    cat_wet=sorted(data_wet_rid_year.select("Cat").unique().to_series().to_list())
    st.session_state.cat_wet=cat_wet
    cat_wet_sel=wet1.multiselect("Selezionare categoria desiderata:", cat_wet, default=cat_wet, key=11)
    data_wet_rid_year_cat=data_wet_rid_year.filter(pl.col("Cat").is_in(cat_wet_sel))
    wet2.write(data_wet_rid_year_cat)
    st.altair_chart(alt.Chart(data_wet_rid_year_cat).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed").scale(zero=False), alt.Color("Rider_Name")),
                use_container_width=True)
```
### 