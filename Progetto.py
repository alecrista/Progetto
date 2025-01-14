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
#######
### BREVE INTRODUZIONE ###
st.header("Introduzione")
st.write("Per direzionare l'utente su cosa o chi analizzare più avanti ecco un'infarinatura dei piloti e delle case costruttrici con più successo tra i 2005 e il 2017, il tutto ovviamente derivato dal dataset originale.")
st.subheader("I piloti più vincenti nel periodo in questione")
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
#######
### CLASSIFICHE GENERALI ###
st.header("Classifiche generali")
st.write("In questa sezione andremo semplicemente a vedere le classifiche finali dei mondiali piloti e costruttori",
" di ogni categoria in un annata a scelta, ovviamente derivando il tutto dal dataset originale.")
st.write("La classifica costruttori tiene conto il punteggio del miglior pilota di ogni costruttore in ogni Gran Premio, sommando il tutto per ogni costruttore.")
st.write("**Sistema di punteggio:**")
col1, col2=st.columns(2)
points=sorted(data.select(pl.col("Points").round().unique()).drop_nulls().to_series().to_list())
points.remove(0)
col1.write("Posizione")
col2.write("Punti")
for i in range(len(points)):
    col1.write(i+1) #posizione
    col2.write(int(points[-i-1])) #punti
st.write("In caso di gara interrotta con meno di 2/3 della distanza di gara percorsi e gara non ripresa vengono assegnati punti dimezzati.")
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
########
### CLASSIFICHE PER OGNI GP ###
st.header("Risultati di ogni GP per categoria")
st.write("Se si seleziona la modalità Gran Premio - Anno allora si dovrà selezionare un'annata e poi il/i Gran Premio/i che l'utente vuole visualizzare."
         " Se si seleziona la modalità Per data allora si dovrà selezionare una data compresa tra l'1 gennaio 2005 e il 31 dicembre 2017."
         " In quest'ultimo caso si consiglia di selezionare quasi sempre domeniche, tranne nei casi in cui il Gran Premio d'Olanda si correva"
         " l'ultimo sabato di Giugno nel periodo 2005-2015. Dal 2016 è sempre stata l'ultima domenica del mese."
         " Un altro caso di GP non domenicale è quello del GP di Qatar del 2009, dove la classe MotoGP ha corso di lunedì (più precisamente il 13 aprile)."
         " Infine da notare che nella modalità Per data, la nazionalità del GP di cui si stanno osservando i risultati si trova nella colonna GP."
)
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

########
### ANALISI PER PILOTA ###
st.header("Analisi per pilota")
##
st.subheader("Piloti e punti conquistati")
st.write("Analisi effettuata sui piloti per mettere a confronto le loro annate più e meno di successo, attraverso il confronto dei punteggi per ognuno di loro alla fine di ogni stagione."
         " Si consiglia di selezionare prima il pilota e poi eventualmente la/e categoria/e.")
st.write("In caso di difficoltà nella comprensione del grafico si consiglia di dare un'occhiata alla tabella con i dati ricercati dall'utente, dalla quale deriva poi il grafico.")
data_rider_points=data.group_by("Rider_Name","Year","Category").agg(pl.col("Points").sum(), pl.col("Bike").implode().list.unique()).sort("Rider_Name", "Year", descending=True)
data_rider_points=data_rider_points.drop_nulls() #dataset dei punteggi di ogni pilota in ogni stagione
col111, col112=st.columns(2)
rider_list=sorted(data.select(pl.col("Rider_Name").unique()).drop_nulls().to_series().to_list()) #lista di selezione piloti
st.session_state.rider_list=rider_list #salvo la lista a session state per sicurezza
riders=col111.multiselect("Inserire piloti desiderati:", rider_list, default="Valentino ROSSI") #operatore di filtraggio per pilota
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

##
st.subheader("Piloti e velocità dura e pura")
st.write("Mettiamo a confronto invece le velocità dei vari piloti nel corso di ogni stagione, così per vedere se la regola che dice che non vince il più veloce (regola tipica del motorsport) effettivamente è vera."
         " Verranno svolte 2 analisi, una per condizioni di pista asciutta e una per condizioni di pista bagnata.")
st.write("La variabile Cat è riassuntiva della variabile category: raggruppa 125cc e Moto3 nell'unica modalità Lightweight e 250cc e Moto2 nell'unica modalità Middleweight, questo per facilitare l'analisi e per confrontare"
         " anche, sebbene sulla stessa linea, i cambi da motori 2 tempi delle 125 e delle 250 ai motori 4 tempi delle Moto3 e delle Moto2.")
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
rid_dry_sel=dry1.multiselect("Selezionare pilota/i desiderato/i:", rid_dry, default="Jorge LORENZO")
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
rid_wet_sel=wet1.multiselect("Selezionare pilota desiderato", rid_wet, default="Marc MARQUEZ")
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
##
st.subheader("Piloti e numeri di gara")
st.write("Con questa curiosa analisi si vuole vedere il rapporto tra i piloti e i numeri di gara stampati sulle loro moto. Da notare ovviamente che il numero 1"
         "  stato usato solo da campioni del mondo che hanno difeso la corona l'anno dopo e che Dani Pedrosa è stato tra i pochissimi, se non l'unico,"
         " che ha corso anche con il 2 e il 3 basandosi sul risultato dell'anno precedente (2 in base al secondo posto del 2007 e 3 in pase al terzo del 2008).")
rid_numbers=sorted(data.select(pl.col("Rider_Number").unique()).drop_nulls().to_series().to_list())
for i in range(len(rid_numbers)):
    rid_numbers[i]=int(rid_numbers[i]) #trasformo gli elementi dela lista da decimali ad interi
st.session_state.rid_numbers=rid_numbers #"salvo" la lista di numeri di piloti
d_rid_num=data.group_by("Rider_Name","Rider_Number").agg(pl.col("Rider_Number").count().alias("N_races")).drop_nulls().sort(
    pl.col("Rider_Name"), descending=False) #dataset con tutti i piloti e tutti i loro numeri di gara
st.write("**Analisi in base al numero**")
num1, num2=st.columns(2)
num1.write("Andiamo a guardare il rapporto tra piloti e i numeri sulle carene delle loro moto, osservando per quante gare ad esempio sono durati i rispettivi connubi.")
num=int(num2.selectbox("Inserire numero da analizzare:", rid_numbers))
d_rid_num_filt=d_rid_num.filter(pl.col("Rider_Number")==num) #dataset filtrato in base al numero
num1.write(d_rid_num_filt)
num_chart=alt.Chart(d_rid_num_filt).mark_arc(innerRadius=50).encode(alt.Theta("N_races"), alt.Color("Rider_Name"), alt.Text("N_races"))
num2.altair_chart(num_chart, use_container_width=True)
st.write("**Analisi in base ai piloti**")
num11, num12=st.columns(2)
rid_list=sorted(d_rid_num.select(pl.col("Rider_Name").unique()).drop_nulls().to_series().to_list())
st.session_state.rid_list=rid_list #"salvo" la lista di piloti
rid=num11.selectbox("Inserire pilota desiderato", rid_list)
d_rid_num_2=d_rid_num.filter(pl.col("Rider_Name")==rid) #dataset filtrato in base al pilota
rid_chart=alt.Chart(d_rid_num_2).mark_arc(innerRadius=50).encode(alt.Theta("N_races"), alt.Color("Rider_Number"), alt.Text("N_races"))
#curiosamente Altair sceglie di usare la scala "log", questo perché gli si dice di cambiare colore in base ad un numero probabilmente.
num11.write(d_rid_num_2.sort(pl.col("N_races"), descending=True))
num12.altair_chart(rid_chart, use_container_width=True)
##
### SVOLGO ANALISI SIMILI MA CON I COSTRUTTORI. ###
st.header("Analisi per costruttore")
st.subheader("Costruttori e punti medi")
st.write("Per i costruttori, giusto per cambiare e volendo anche fare un'analisi un po' più precisa, ragioneremo con i punti medi di ogni costruttore per stagione."
         " ATTENZIONE: NON E' UN'ANALISI VERAMENTE CORRETTA. Questo perché nel Motomondiale, per la classifica costruttori, viene tenuto conto solo dei punteggi dei migliori piloti di ogni costruttore in ogni GP."
         " Se ad esempio una classifica dice: 1 Marquez (Honda) 25 pts, 2 Dovizioso (Ducati) 20 pts, 3 Pedrosa (Honda) 16 pts, ecc.,  nella classifica costruttori, per le case Honda e Ducati, conteranno solo i punteggi di Marquez per Honda e di Dovizioso per Ducati e così via.")
st.write("Tra le chicche che sono da notare è il confronto Yamaha-Honda-Ducati in MotoGP nel 2017: quell'anno Honda vinse mondiale piloti e costruttori,"
                 " tuttavia Yamaha risulta essere la moto che ottenne più punti in media per GP. Questo perché Yamaha corse con solo 4 moto, tutte e 4"
                 " pressoché competitive, mentre Honda corse con 5 moto, 2 delle quali finirono fuori dalla top 10 del mondiale piloti e Ducati con ben 8"
                 " moto, 5 delle quali finirono fuori dalla top-10. Probabilmente quindi le eccessive frequenze di moto Ducati e Honda o le ridotte frequenze"
                 " di moto Yamaha fecero in modo che Yamaha ottenesse più punti in media per GP. Questo però non infulisce sulla classifica costruttori, poiché"
                 " essa prende solo i migliori punteggi di ciascun costruttore per ciascun Gran Premio."
                 " Da notare poi che nella classe Middleweight tutti i costruttori pre esistenti cessano di esistere. Questo perché dal 2010 entrò in vigore l'attuale"
                 " categoria Moto2, con moto equipaggiate di motori Honda 600cc, con radicali cambi di costruttori che quindi furono tutti solo fornitori di telai."
                 )
data_cons=data.group_by("Year",pl.col("Bike").alias("Constructor"),"Category").agg(pl.col("Points").mean()).sort("Year","Constructor", descending=False) #Mi creo il dataset su cui far partire l'analisi
#Riunisco Moto2 e 250cc nella categoria "Middleweight" e Moto3 e 125cc nella categoria "Lightweigth"
#creo quindi le liste di anni e categorie e le salvo al server di Streamlit
d_cons=data_cons.with_columns(
        pl.when(pl.col("Category").is_in(["125cc","Moto3"])).then(pl.lit("Lightweight")).otherwise(
            pl.when(pl.col("Category").is_in(["250cc","Moto2"])).then(pl.lit("Middleweight")).otherwise(pl.lit("MotoGP"))
        ).alias("Cat")
    ).select("Year", "Constructor","Points","Cat").drop_nulls()
cons1, cons2=st.columns(2)
#cons2.write(d_cons)
#In cons1 metterò le opzioni di selezione, in cons2 il dataset filtrato.
cons_list=sorted(d_cons.select(pl.col("Constructor").unique()).to_series().to_list())
st.session_state.cons_list=cons_list #salvo la lista dei costruttori
cons_sel=cons1.multiselect("Inserire costruttore/i di interesse: (Attenzione: se si inserisce solo un costruttore che ha corso per solo un anno il programma darà errore, per cui selezionarne per sicurezza anche uno longevo come Aprilia, Honda, Ducati o Yamaha)",
                           cons_list, default="Yamaha")
if len(cons_sel)==0:
    st.write("Inserire almeno un costruttore.")
else:
    d_cons_filt=d_cons.filter(pl.col("Constructor").is_in(cons_sel))
    c_year_list=sorted(d_cons_filt.select(pl.col("Year").unique()).to_series().to_list())
    st.session_state.c_year_list=c_year_list #salvo la lista annate.
    c_year_sel=cons1.slider("Inserire periodo da analizzare:", min_value=c_year_list[0], max_value=max(c_year_list), value=(c_year_list[0], max(c_year_list)), key=7)
    d_cons_year=d_cons_filt.filter(pl.col("Year")<=c_year_sel[1], pl.col("Year")>=c_year_sel[0]) #dataset filtrato per annate
    c_cat_list=sorted(d_cons_year.select(pl.col("Cat").unique()).to_series().to_list())
    st.session_state.c_cat_list=c_cat_list #salvo la lista categorie.
    c_cat_sel=cons1.multiselect("Inserire categoria desiderata:", c_cat_list, default=c_cat_list)
    if len(c_cat_sel)!=0:
        d_cons_year_cat=d_cons_year.filter(pl.col("Cat").is_in(c_cat_sel)) #dataset filtrato per categorie in base all'annata
        cons2.write(d_cons_year_cat)
        st.write("**Confronto grafico per ogni categoria**")
        for i in c_cat_sel:
            d_cons_year_cat_filt=d_cons_year_cat.filter(pl.col("Cat")==str(i))
            #grafico d'aiuto, se così si può chiamare ---v
            cons_ch_filt=alt.Chart(d_cons_year_cat_filt).mark_line().encode(alt.X("Year"), alt.Y("Points").scale(zero=False), alt.Color("Constructor").scale(scheme="viridis"), alt.Text("Points"))
            st.write(i)
            st.altair_chart(cons_ch_filt, use_container_width=True)
    else:
        cons2.write(d_cons_year)
        st.write("**Confronto grafico per ogni categoria**")
        st.write("Per il confronto grafico selezionare almeno una categoria")
#########
st.subheader("Costruttori e velocità medie")
st.write("Quale costruttore ha mostrato più potenziale nel corso di stagione in ogni categoria? Lo scopriamo attraverso questa inusuale ma secondo me utile analisi:",
"andremo infatti a vedere le velocità medie (variabile Avg_Speed) per ogni costruttore in una stagione per ogni categoria in cui esso ha partecipato.",
"Riassumeremo come prima 125 e Moto3 in Lightweight e 250 e Moto2 in Middleweigth.")
st.write("Non verranno mostrati, come con le velocità medie dei piloti, dei grafici generici per ogni condizione di pista, poiché essi pssono essere interpretati sia come media dei piloit che come media dei costruttori, "
"derivando dalle medie generali delle velocità di ogni anno per ogni categoria.")
st.write("Stessa chicca di prima per la classe MotoGP ma con le velocità. Da notare inoltre che Yamaha fu il costruttore più veloce dal 2014, nonostante Honda vinse 14 gare su 18 quell'anno."
                 " Questo perché nel biennio 2014-2015 venne introdotta nella classe MotoGP la sottocategoria Open, con moto più lente che correvano con le MotoGP"
                 " normali, alla quale Honda partecipò con un suo modello. Ovviamente le gare furono vinte dal team ufficiale dotato di Honda normali."
                 " Da notare inoltre il grandissimo step di Yamaha in termini di competitività dal 2007 al 2008, dove passò da essere tra le più lente ad essere la più veloce.")
st.write("Infine notiamo come le velocità della classe MotoGP si riducono dal 2015 al 2016. Questo perché nel 2016 si passò da correre con gomme Bridgestone a gomme Michielin,"
                 " all'inizio meno competitive delle gomme precedenti. Ma non solo: nel 2016 si corsero più gare sul bagnato rispetto al 2015.")                 
data_cons_speed=data.group_by("Year",pl.col("Bike").alias("Constructor"),"Category").agg(pl.col("Avg_Speed").alias("Speed").mean().round(3) #arrotondo alla terza cifra
                  ).sort("Constructor","Year","Category",descending=False)
d_cons_speed=data_cons_speed.with_columns( #dataset con dati riassunti
        pl.when(pl.col("Category").is_in(["125cc","Moto3"])).then(pl.lit("Lightweight")).otherwise(
            pl.when(pl.col("Category").is_in(["250cc","Moto2"])).then(pl.lit("Middleweight")).otherwise(pl.lit("MotoGP"))
        ).alias("Cat")
    ).select("Year", "Constructor","Cat","Speed").drop_nulls()
cons11, cons12=st.columns(2)
#In cons1 metterò le opzioni di selezione, in cons2 il dataset filtrato.
cons_list_2=sorted(d_cons_speed.select(pl.col("Constructor").unique()).to_series().to_list())
st.session_state.cons_list_2=cons_list_2 #salvo un'altra lista costruttori
cons_sel_2=cons11.multiselect("Inserire costruttore/i di interesse:", cons_list_2, default="Honda", key=21)
if len(cons_sel_2)==0:
    st.write("Inserire almeno un costruttore.")
else:
    d_cons_filt_2=d_cons_speed.filter(pl.col("Constructor").is_in(cons_sel_2)) #dataset filtrato in base al costruttore
    c_year_list_2=sorted(d_cons_filt_2.select(pl.col("Year").unique()).to_series().to_list())
    st.session_state.c_year_list_2=c_year_list_2 #salvo un'altra lista di anni
    c_year_sel_2=cons11.slider("Inserire periodo da anlizzare:", min_value=c_year_list_2[0], max_value=max(c_year_list_2), value=(c_year_list_2[0], max(c_year_list_2)), key=8)
    d_cons_speed_year=d_cons_filt_2.filter(pl.col("Year")<=c_year_sel_2[1], pl.col("Year")>=c_year_sel_2[0])
    c_cat_list_2=sorted(d_cons_speed_year.select(pl.col("Cat").unique()).to_series().to_list())
    st.session_state.c_cat_list_2=c_cat_list_2 #salvo una lista di categorie
    c_cat_sel_2=cons11.multiselect("Inserire categoria desiderata:", c_cat_list_2, default=c_cat_list_2, key=12)
    if len(c_cat_sel_2)!=0:
        #dataset filtrato in base alla categoria ---v
        d_cons_speed_year_cat=d_cons_speed_year.filter(pl.col("Cat").is_in(c_cat_sel_2)).sort("Year", "Constructor", descending=False)
        cons12.write(d_cons_speed_year_cat)
        st.write("**Confronto grafico per ogni categoria**")
        for i in c_cat_sel_2:
            d_cons_speed_year_cat_filt=d_cons_speed_year_cat.filter(pl.col("Cat")==str(i))
            cons_ch_filt_2=alt.Chart(d_cons_speed_year_cat_filt).mark_line().encode(alt.X("Year"), alt.Y("Speed").scale(zero=False), alt.Color("Constructor"), alt.Text("Speed"))
            st.write(i)
            if len(c_year_list_2)>1:
                st.altair_chart(cons_ch_filt_2, use_container_width=True)
            else:
                st.write("Con una sola rilevazione nel tempo non è possibile eseguire un'analisi grafica.")
    else:
        cons12.write(d_cons_speed_year)
        st.write("**Confronto grafico per ogni categoria**")
        st.write("Per il confronto grafico selezionare almeno una categoria.")
######### CAMBIAMO COMPLETAMENTE UNITA' STATISTICA #########
st.header("Analisi per piste")
st.subheader("Ohi, que calor!")
st.write("In questa sezione confronteremo le varie temperature medie di asfalto e aria per ogni pista, tenendo un minimo conto anche del periodo in cui si corre e anche delle condizioni della pista (asciutta o bagnata).")
#dataset raggruppato con tutte le temperature di aria e asfalto rilevate per ogni pista in ogni anno -----v
data_track_temp=data.group_by("Year", pl.col("GP").alias("Track"), "Date","Track_Condition").agg(pl.col("Track_Temp").mean(), pl.col("Air_Temp").mean()).sort("Year","Track","Track_Condition",descending=False)
wet_dry=st.selectbox("Inserire condizione di pista desiderata:", ["Dry", "Wet"])
st.write("Dry: Asciutto, Wet: Bagnato")
if wet_dry=="Dry":
    data_track_temp_d=data_track_temp.filter(pl.col("Track_Condition")=="Dry") #dataset con temperature rilevate con pista asciutta
    trk1, trk2=st.columns(2)
    trk_list=sorted(data_track_temp_d.select("Track").unique().to_series().to_list())
    st.session_state.trk_list=trk_list #salvo la lista di tracciati
    trk_filt=trk1.multiselect("Selezionare pista/e d'interesse:", trk_list, default=trk_list[0])
    data_track_temp_d_filt=data_track_temp_d.filter(pl.col("Track").is_in(trk_filt))
    trk_year_list=sorted(data_track_temp_d_filt.select("Year").unique().to_series().to_list())
    st.session_state.trk_year_list=trk_year_list #salvo la lista di annate (dataset dei tracciati asciutti)
    year_filt=trk2.slider("Selezionare periodo d'interesse:", min_value=trk_year_list[0], max_value=max(trk_year_list), value=(trk_year_list[0], max(trk_year_list)),key=55)
    data_track_temp_d_final=data_track_temp_d_filt.filter(pl.col("Year")<=year_filt[1], pl.col("Year")>=year_filt[0])
    if len(trk_filt)==0:
        st.write("Selezionare almeno una pista.")
    else:
        trk_chart_d_ttemp=alt.Chart(data_track_temp_d_final).mark_line().encode(
            alt.X("Year"), alt.Y("Track_Temp").scale(zero=False), alt.Color("Track"), alt.Text("Track_Temp")) #grafico temperatura asfalto
        trk_chart_d_atemp=alt.Chart(data_track_temp_d_final).mark_line().encode(
            alt.X("Year"), alt.Y("Air_Temp").scale(zero=False), alt.Color("Track"), alt.Text("Air_Temp")) #grafico temperatura aria
        st.write(data_track_temp_d_final)
        st.write("**Temperature asfalto**")
        st.altair_chart(trk_chart_d_ttemp, use_container_width=True)
        st.write("**Temperature aria**")
        st.altair_chart(trk_chart_d_atemp, use_container_width=True)
else:
    #stessa identica analisi ma con bista bagnata. Alcune variabili, operatori di filtraggio o dataset filtrati avranno la parola w o wet per classificarli come "pista bagnata"
    data_track_temp_w=data_track_temp.filter(pl.col("Track_Condition")=="Wet")
    trk1, trk2=st.columns(2)
    trk_list=sorted(data_track_temp_w.select("Track").unique().to_series().to_list())
    st.session_state.trk_list=trk_list #salvo la lista circuiti
    trk_filt=trk1.multiselect("Selezionare pista/e d'interesse:", trk_list, default=trk_list[0])
    data_track_temp_w_filt=data_track_temp_w.filter(pl.col("Track").is_in(trk_filt))
    trk_year_list=sorted(data_track_temp_w_filt.select("Year").unique().to_series().to_list())
    st.session_state.trk_year_list=trk_year_list #salvo la lista annate
    year_filt=trk2.slider("Selezionare periodo d'interesse:", min_value=trk_year_list[0], max_value=max(trk_year_list), value=(trk_year_list[0], max(trk_year_list)),key=65)
    data_track_temp_w_final=data_track_temp_w_filt.filter(pl.col("Year")<=year_filt[1], pl.col("Year")>=year_filt[0])
    if len(trk_filt)==0:
        st.write("Selezionare almeno una pista.")
    else:
        trk_chart_d_ttemp=alt.Chart(data_track_temp_w_final).mark_line().encode(
            alt.X("Year"), alt.Y("Track_Temp").scale(zero=False), alt.Color("Track"), alt.Text("Track_Temp")) #grafico temperatura asflato
        trk_chart_d_atemp=alt.Chart(data_track_temp_w_final).mark_line().encode(
            alt.X("Year"), alt.Y("Air_Temp").scale(zero=False), alt.Color("Track"), alt.Text("Air_Temp")) #grafico temperatura aria
        st.write(data_track_temp_w_final)
        st.write("**Temperature asfalto**")
        st.altair_chart(trk_chart_d_ttemp, use_container_width=True)
        st.write("**Temperature aria**")
        st.altair_chart(trk_chart_d_atemp, use_container_width=True)
##
st.subheader("Piste-aeroporti")
st.write(
    "In questa sezione confronteremo, come fatto già numerose volte in precedenza, le velocità medie. Questa volta, distingueremo tutto anche per categoria, "
    "sempre riassumendo 125 e Moto3 in Lightweight e 250 e Moto2 in Middleweight. Il tutto sarà accompagnato da una rappresentazione grafica per ogni categoria."
    )
#dataset con tutte le velocità medie di tutte le pista in tutte le condizioni di ogni anno ----vv
data_trk_speed=data.group_by("Year",pl.col("GP").alias("Track"),"Category","Track_Condition").agg(pl.col("Avg_Speed").mean().alias("Speed"))
data_trk_speed=data_trk_speed.with_columns( #dataset con categorie raggruppate
        pl.when(pl.col("Category").is_in(["125cc","Moto3"])).then(pl.lit("Lightweight")).otherwise(
            pl.when(pl.col("Category").is_in(["250cc","Moto2"])).then(pl.lit("Middleweight")).otherwise(pl.lit("MotoGP"))
        ).alias("Cat")
    ).select("Year", "Track","Cat","Track_Condition","Speed").drop_nulls() #elimino valori nulli e superflui
wet_dry=st.selectbox("Inserire condizione di pista desiderata", ["Dry", "Wet"], key=69)
st.write("Dry: Asciutto, Wet: Bagnato")
if wet_dry=="Dry":
    d_t_speed_d=data_trk_speed.filter(pl.col("Track_Condition")=="Dry") #dataset di velocità medie con pista asciutta
    trk_list_2=sorted(d_t_speed_d.select(pl.col("Track").unique()).to_series().to_list())
    st.session_state.trk_list_2=trk_list_2 #salvo la lista tracciati
    trk11, trk12=st.columns(2)
    trk_d_filt=trk11.multiselect("Inserire pista:", trk_list_2,default=trk_list_2[0],key=32) #metto un default per vedere cosa avrò in output
    if len(trk_d_filt)==0:
        st.write("Inserire almeno una pista.")
    else:
        d_t_speed_d_filt=d_t_speed_d.filter(pl.col("Track").is_in(trk_d_filt)) #dataset filtrato in base ai tracciati
        t_year_list=sorted(d_t_speed_d_filt.select(pl.col("Year").unique()).to_series().to_list())
        st.session_state.t_year_list=t_year_list #salvo la lista annate (dataset tracciati)
        t_year_filt=trk11.slider("Inserire periodo desiderato:", min_value=t_year_list[0], max_value=max(t_year_list), value=(t_year_list[0], max(t_year_list)), key=42)
        d_t_speed_d_final=d_t_speed_d_filt.filter(pl.col("Year")<=t_year_filt[1], pl.col("Year")>=t_year_filt[0]) #dataset filtrato in base alle annate, dati i tracciati
        st.write(d_t_speed_d_final.sort("Year", "Cat", descending=False))
        cat_trk_list=sorted(d_t_speed_d_final.select(pl.col("Cat").unique()).to_series().to_list())
        st.session_state.cat_trk_list=cat_trk_list #salvo la lista delle categorie (dataset tracciati)
        st.write("**_Analisi grafica delle velocità:_**")
        for i in cat_trk_list:
            d_t_speed_d_final_cat=d_t_speed_d_final.filter(pl.col("Cat")==str(i)) #dataset filtrato per categoria
            t_speed_chart_d_cat=alt.Chart(d_t_speed_d_final_cat).mark_line().encode(
                alt.X("Year"), alt.Y("Speed").scale(zero=False), alt.Color("Track"), alt.Text("Speed") #grafico finale di una categoria
                )
            st.write(str(i))
            st.altair_chart(t_speed_chart_d_cat, use_container_width=True)
else:
    #stessa identica analisi con condizioni di pista bagnata. Come sempre si sostituiranno nella nomenclatura di operatori di filtraggio, dataset o variabili
    #le parole d o dry con le parole w o wet. 
    d_t_speed_w=data_trk_speed.filter(pl.col("Track_Condition")=="Wet")
    trk_list_2=sorted(d_t_speed_w.select(pl.col("Track").unique()).to_series().to_list())
    st.session_state.trk_list_2=trk_list_2 #salvo la lista tracciati
    trk11, trk12=st.columns(2)
    trk_w_filt=trk11.multiselect("Inserire pista:", trk_list_2,default=trk_list_2[0],key=33)
    if len(trk_w_filt)==0:
        st.write("Inserire almeno una pista!")
    else:
        d_t_speed_w_filt=d_t_speed_w.filter(pl.col("Track").is_in(trk_w_filt))
        t_year_list=sorted(d_t_speed_w_filt.select(pl.col("Year").unique()).to_series().to_list())
        st.session_state.t_year_list=t_year_list #salvo la lista annate (in base al dataset tracciati)
        t_year_filt=trk11.slider("Inserire periodo desiderato:", min_value=t_year_list[0], max_value=max(t_year_list), value=(t_year_list[0], max(t_year_list)), key=42)
        d_t_speed_w_final=d_t_speed_w_filt.filter(pl.col("Year")<=t_year_filt[1], pl.col("Year")>=t_year_filt[0]) #dati filtrati in base al periodo
        st.write(d_t_speed_w_final.sort("Year", "Cat", descending=False))
        cat_trk_list=sorted(d_t_speed_w_final.select(pl.col("Cat").unique()).to_series().to_list())
        st.session_state.cat_trk_list=cat_trk_list #salvo la lista categorie (in base al dataset tracciati)
        st.write("**_Analisi grafica delle velocità con pista bagnata:_**")
        for i in cat_trk_list:
            d_t_speed_w_final_cat=d_t_speed_w_final.filter(pl.col("Cat")==str(i)) #dataset filtrato per categoria
            t_speed_chart_w_cat=alt.Chart(d_t_speed_w_final_cat).mark_line().encode(
                alt.X("Year"), alt.Y("Speed").scale(zero=False), alt.Color("Track"), alt.Text("Speed") #grafico della velocità media di una singola categoria
                )
            st.write(str(i))
            st.altair_chart(t_speed_chart_w_cat, use_container_width=True)
#####
st.title("**_THAT'S ALL FOLKS!_**")