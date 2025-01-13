import streamlit as st
import altair as alt
import polars as pl
import datetime as dt
import pandas as pd
import math as mt
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
    pl.col("Rider_Name").str.replace("Daniel PEDROSA","Dani PEDROSA").alias("Rider_Name")
)
#######
### BREVE INTRODUZIONE ###
st.header("Introduzione")
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
st.write("**Sistema di punteggio:**")
col1, col2=st.columns(2)
points=sorted(data.select(pl.col("Points").round().unique()).drop_nulls().to_series().to_list())
points.remove(0)
col1.write("Posizione")
col2.write("Punti")
for i in range(len(points)):
    col1.write(i+1) #posizione
    col2.write(points[-i-1]) #punti
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
mod=st.selectbox("Inserire modalità di filtraggio", ["Gran Premio - Anno", "Per data"])
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
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","Year", "TRK", "Track").sort("Position", descending=False)
        col11.write(d1) #risultati MotoGP
        d2=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["250cc", "Moto2"])).filter(pl.col("Year")==year1).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","Year", "TRK", "Track").sort("Position", descending=False)
        col12.write(d2) #risultati Moto2/250cc
        d3=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["125cc", "Moto3"])).filter(pl.col("Year")==year1).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","Year", "TRK", "Track").sort("Position", descending=False)
        col13.write(d3) #risultati Moto3/125cc
elif mod==str("Per data"):
    data_amg=st.date_input("Inserire data:", min_value=dt.date(2005, 1, 1), max_value=dt.date(2017, 12, 31))
    st.write("_*Selezionare una Domenica. In caso di tabelle vuote vuol dire che in quella data non è stato corso nessun gran premio.*_")
    data_date=data.with_columns(pl.col("Date").str.strptime(pl.Date, "%Y-%m-%d").alias("PyDate"))
    col11, col12, col13=st.columns(3)
    d1=data_date.filter(pl.col("PyDate")==data_amg).filter(pl.col("Category")=="MotoGP").filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","TRK","PyDate").sort("Position", descending=False)
    col11.write(d1) #risultati MotoGP
    d2=data_date.filter(pl.col("PyDate")==data_amg).filter(pl.col("Category").is_in(["250cc", "Moto2"])).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","TRK","PyDate").sort("Position", descending=False)
    col12.write(d2) #risultati Moto2/250cc
    d3=data_date.filter(pl.col("PyDate")==data_amg).filter(pl.col("Category").is_in(["125cc", "Moto3"])).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","TRK","PyDate").sort("Position", descending=False)
    col13.write(d3) #risultati Moto3/125cc

########
### ANALISI PER PILOTA ###
st.header("Analisi per pilota")
##
st.subheader("Piloti e punti conquistati")
st.write("Analisi effettuata sui piloti, non sulle categorie. Per cui selezionare prima il pilota e poi eventualmente la/e categoria/e")
data_rider_points=data.group_by("Rider_Name","Year","Category").agg(pl.col("Points").sum(), pl.col("Bike").implode().list.unique()).sort("Rider_Name", "Year", descending=True)
data_rider_points=data_rider_points.drop_nulls() #dataset dei punteggi di ogni pilota in ogni stagione
col111, col112=st.columns(2)
rider_list=sorted(data.select(pl.col("Rider_Name").unique()).drop_nulls().to_series().to_list()) #lista di selezione piloti
st.session_state.rider_list=rider_list #salvo la lista a session state per sicurezza
riders=col111.multiselect("Inserire piloti desiderati:", rider_list) #operatore di filtraggio per pilota
d_filt_1=data_rider_points.filter(pl.col("Rider_Name").is_in(riders)) #dataset filtrato per pilota
if len(riders)!=0:
    cat_list=sorted(d_filt_1.select(pl.col("Category").unique()).to_series().to_list()) #lista di selezione categorie
    category=col112.multiselect("Inserire Categoria desiderata:", cat_list, default=cat_list) #operatore di filtraggio per categoria
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
data_rider_speed=data.group_by("Rider_Name","Year","Category","Bike","Track_Condition").agg(
    pl.col("Avg_Speed").mean()).sort("Rider_Name", "Year", descending=True).filter(pl.col("Avg_Speed")>0) #Così rimuovo i dati assenti
#
st.write("__*Pista asciutta*__")
mud=data_rider_speed.filter(pl.col("Track_Condition")=="Dry").select(pl.col("Avg_Speed").mean())[0,0] #più conveniente di numpy
st.write("Velocità media di tutti i piloti:", mud)
d_dry=data_rider_speed.filter(pl.col("Track_Condition")=="Dry")
d_dry_gen=d_dry.group_by("Year","Category").agg(pl.col("Avg_Speed").mean()).sort("Year","Category", descending=False)
d_dry_gen=d_dry_gen.with_columns(
    pl.when(pl.col("Category").is_in(["125cc","Moto3"]))
    .then(pl.lit("Lightweight"))
    .otherwise(pl.when(pl.col("Category").is_in(["250cc","Moto2"]))
               .then(pl.lit("Middleweight"))
               .otherwise(pl.lit("MotoGP")))
               .alias("Cat"))
dry1, dry2=st.columns(2)
dry1.write(d_dry_gen.sort("Year",descending=False).sort("Cat", descending=True))
chart_dry=alt.Chart(d_dry_gen).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed").scale(zero=False), alt.Color("Cat").scale(domain=['Lightweight', 'Middleweight', 'MotoGP'], range=['#FF0000', '#00FF00', '#0000FF']))
dry2.altair_chart(chart_dry, use_container_width=False)
st.write("Svolgiamo un'analisi pilota per pilota.")
dry1, dry2=st.columns(2)
d_dry_rid=d_dry.group_by("Year","Category","Rider_Name","Bike").agg(pl.col("Avg_Speed").mean()).sort("Year","Rider_Name","Category", descending=False)
d_dry_rid=d_dry_rid.with_columns(
    pl.when(pl.col("Category").is_in(["125cc","Moto3"]))
    .then(pl.lit("Lightweight"))
    .otherwise(pl.when(pl.col("Category").is_in(["250cc","Moto2"]))
               .then(pl.lit("Middleweight"))
               .otherwise(pl.lit("MotoGP")))
               .alias("Cat"))
rid_dry=sorted(d_dry_rid.select("Rider_Name").unique().to_series().to_list()) 
st.session_state.rid_dry=rid_dry #"salvo" la lista di piloti attraverso session_state
rid_dry_sel=dry1.multiselect("Selezionare pilota desiderato", rid_dry)
if len(rid_dry_sel)==0:
    st.write("Inserire almeno un pilota")
else:
    data_dry_rid=d_dry_rid.filter(pl.col("Rider_Name").is_in(rid_dry_sel))
    year_dry=sorted(data_dry_rid.select("Year").unique().to_series().to_list())
    year_dry_sel=dry1.slider("Selezionare periodo desiderato:", min_value=year_dry[0], max_value=max(year_dry), value=(year_list[0], max(year_list)))
    data_dry_rid_year=data_dry_rid.filter(pl.col("Year")>=year_dry_sel[0], pl.col("Year")<=year_dry_sel[1])
    cat_dry=sorted(data_dry_rid_year.select("Cat").unique().to_series().to_list())
    cat_dry_sel=dry1.multiselect("Selezionare categoria desiderata", cat_dry, default=cat_dry)
    data_dry_rid_year_cat=data_dry_rid_year.filter(pl.col("Cat").is_in(cat_dry_sel))
    dry2.write(data_dry_rid_year_cat)
    st.altair_chart(alt.Chart(data_dry_rid_year_cat).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed").scale(zero=False), alt.Color("Rider_Name")),
                use_container_width=True)
### RIPETO LO STESSO PROCEDIMENTO ANCHE CON PISTA BAGNATA
st.write("__*Pista bagnata*__")
muw=data_rider_speed.filter(pl.col("Track_Condition")=="Wet").select(pl.col("Avg_Speed").mean())[0,0]
#più conveniente di numpy
st.write("Velocità media ti tutti i piloti:", muw)
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
chart_wet=alt.Chart(d_wet_gen).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed").scale(zero=False), alt.Color("Cat").scale(domain=['Lightweight', 'Middleweight', 'MotoGP'], range=['#FF0000', '#00FF00', '#0000FF']))
wet2.altair_chart(chart_wet, use_container_width=False)
st.write("Da notare che curiosamente, tra inizio 2012 e metà 2014, la classe leggera, probablimente perché ha corso meno gare e con un asfalto non completamente bagnato.")
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
st.session_state.rid_wet=rid_wet #"salvo" per sicurezza la lista di biloti (dataset pista bagnata)
rid_wet_sel=wet1.multiselect("Selezionare pilota desiderato", rid_wet)
if len(rid_wet_sel)==0:
    st.write("Inserire almeno un pilota")
else:
    data_wet_rid=d_wet_rid.filter(pl.col("Rider_Name").is_in(rid_wet_sel))
    year_wet=sorted(data_wet_rid.select("Year").unique().to_series().to_list())
    year_wet_sel=wet1.slider("Selezionare periodo da analizzare:", min_value=year_wet[0], max_value=max(year_wet), value=(year_wet[0],max(year_wet)), key=3)
    data_wet_rid_year=data_wet_rid.filter(pl.col("Year")<=year_wet_sel[1], pl.col("Year")>=year_wet_sel[0])
    cat_wet=sorted(data_wet_rid_year.select("Cat").unique().to_series().to_list())
    cat_wet_sel=wet1.multiselect("Selezionare categoria desiderata:", cat_wet, default=cat_wet, key=11)
    data_wet_rid_year_cat=data_wet_rid_year.filter(pl.col("Cat").is_in(cat_wet_sel))
    wet2.write(data_wet_rid_year_cat)
    st.altair_chart(alt.Chart(data_wet_rid_year_cat).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed").scale(zero=False), alt.Color("Rider_Name")),
                use_container_width=True)
##
st.subheader("Piloti e numeri di gara")
rid_numbers=sorted(data.select(pl.col("Rider_Number").unique()).drop_nulls().to_series().to_list())
st.session_state.rid_numbers=rid_numbers #"salvo" la lista di numeri di piloti
d_rid_num=data.group_by("Rider_Name","Rider_Number").agg(pl.col("Rider_Number").count().alias("N_races")).drop_nulls().sort(
    pl.col("Rider_Name"), descending=False)
st.write("**Analisi in base al numero**")
num1, num2=st.columns(2)
num1.write("Andiamo a guardare il rapporto tra piloti e i numeri sulle carene delle loro moto, osservando per quante gare ad esempio sono durati i rispettivi connubi.")
num=int(num2.select_slider("Inserire numero da analizzare:", rid_numbers))
d_rid_num_filt=d_rid_num.filter(pl.col("Rider_Number")==num)
num1.write(d_rid_num_filt)
num_chart=alt.Chart(d_rid_num_filt).mark_arc(innerRadius=50).encode(alt.Theta("N_races"), alt.Color("Rider_Name"), alt.Text("N_races"))
num2.altair_chart(num_chart, use_container_width=True)
st.write("**Analisi in base ai piloti**")
num11, num12=st.columns(2)
rid_list=sorted(d_rid_num.select(pl.col("Rider_Name").unique()).drop_nulls().to_series().to_list())
st.session_state.rid_list=rid_list #"salvo" la lista di piloti
rid=num11.selectbox("Inserire pilota desiderato", rid_list)
d_rid_num_2=d_rid_num.filter(pl.col("Rider_Name")==rid)
rid_chart=alt.Chart(d_rid_num_2).mark_arc(innerRadius=50).encode(alt.Theta("N_races"), alt.Color("Rider_Number"), alt.Text("N_races"))
num11.write(d_rid_num_2.sort(pl.col("N_races"), descending=True))
num12.altair_chart(rid_chart, use_container_width=True)
##
### SVOLGO ANALISI SIMILI MA CON I COSTRUTTORI. ###
st.header("Analisi per costruttore")
st.subheader("Costruttori e punti medi")
st.write("Per i costruttori, giusto per cambiare e volendo anche fare un'analisi un po' più precisa, ragioneremo con i punti medi per stagione")
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
cons_sel=cons1.multiselect("Inserire costruttore/i di interesse", cons_list)
if len(cons_sel)==0:
    st.write("Inserire almeno un costruttore.")
else:
    cons1.write("Tra le chicche che sono da notare è il confronto Yamaha-Honda-Ducati in MotoGP nel 2017: quell'anno Honda vinse mondiale piloti e costruttori,"
                 " tuttavia Yamaha risulta essere la moto che ottenne più punti in media per GP. Questo perché Yamaha corse con solo 4 moto, tutte e 4"
                 " pressoché competitive, mentre Honda corse con 5 moto, 2 delle quali finirono fuori dalla top 10 del mondiale piloti e Ducati con ben 8"
                 " moto, 5 delle quali finirono fuori dalla top-10. Probabilmente quindi le eccessive frequenze di moto Ducati e Honda o le ridotte frequenze"
                 " di moto Yamaha fecero in modo che Yamaha ottenesse più punti in media per GP. Questo però non infulisce sulla classifica costruttori, poiché"
                 " essa prende solo i migliori punteggi di ciascun costruttore per ciascun Gran Premio."
                 " Da notare poi che nella classe Middleweight tutti i costruttori pre esistenti cessano di esistere. Questo perché dal 2010 entrò in vigore l'attuale"
                 " categoria Moto2, con moto equipaggiate di motori Honda 600cc, con radicali cambi di costruttori che quindi furono tutti solo fornitori di telai.")
    d_cons_filt=d_cons.filter(pl.col("Constructor").is_in(cons_sel))
    c_year_list=sorted(d_cons_filt.select(pl.col("Year").unique()).to_series().to_list())
    c_year_sel=cons1.slider("Inserire periodo da analizzare:", min_value=c_year_list[0], max_value=max(c_year_list), value=(c_year_list[0], max(c_year_list)), key=7)
    d_cons_year=d_cons_filt.filter(pl.col("Year")<=c_year_sel[1], pl.col("Year")>=c_year_sel[0])
    c_cat_list=sorted(d_cons_year.select(pl.col("Cat").unique()).to_series().to_list())
    c_cat_sel=cons1.multiselect("Inserire categoria desiderata:", c_cat_list, default=c_cat_list)
    if len(c_cat_sel)!=0:
        d_cons_year_cat=d_cons_year.filter(pl.col("Cat").is_in(c_cat_sel))
        cons2.write(d_cons_year_cat)
        st.write("**Confronto grafico per ogni categoria**")
        for i in c_cat_sel:
            d_cons_year_cat_filt=d_cons_year_cat.filter(pl.col("Cat")==str(i))
            cons_ch_filt=alt.Chart(d_cons_year_cat_filt).mark_line().encode(alt.X("Year"), alt.Y("Points").scale(zero=False), alt.Color("Constructor").scale(scheme="viridis"), alt.Text("Points"))
            st.write(i)
            st.altair_chart(cons_ch_filt, use_container_width=True)
    else:
        cons2.write(d_cons_year)
        st.write("**Confronto grafico per ogni categoria**")
        st.write("Per il confronto grafico selezionare almeno una categoria")
#########
st.subheader("Costruttori e velocità (medie) massime")
st.write("Quale costruttore ha mostrato più potenziale nel corso di stagione in ogni categoria? Lo scopriamo attraverso questa inusuale ma secondo me utile analisi:",
"Andremo infatti a vedere le velocità medie (variabile Avg_Speed) per ogni costruttore in una stagione per ogni categoria in cui esso ha partecipato.")
data_cons_speed=data.group_by("Year",pl.col("Bike").alias("Constructor"),"Category").agg(pl.col("Avg_Speed").alias("Speed").mean().round(3)
                  ).sort("Constructor","Year","Category",descending=False)
d_cons_speed=data_cons_speed.with_columns(
        pl.when(pl.col("Category").is_in(["125cc","Moto3"])).then(pl.lit("Lightweight")).otherwise(
            pl.when(pl.col("Category").is_in(["250cc","Moto2"])).then(pl.lit("Middleweight")).otherwise(pl.lit("MotoGP"))
        ).alias("Cat")
    ).select("Year", "Constructor","Cat","Speed").drop_nulls()
cons11, cons12=st.columns(2)
#cons2.write(d_cons)
#In cons1 metterò le opzioni di selezione, in cons2 il dataset filtrato.
cons_list_2=sorted(d_cons_speed.select(pl.col("Constructor").unique()).to_series().to_list())
st.session_state.cons_list_2=cons_list_2 #salvo un'altra lista costruttori
cons_sel_2=cons11.multiselect("Inserire costruttore/i di interesse:", cons_list_2, key=21)
if len(cons_sel_2)==0:
    st.write("Inserire almeno un costruttore.")
else:
    cons11.write("Stessa chicca di prima per la classe MotoGP ma con le velocità. Da notare inoltre che Yamaha fu il costruttore più veloce dal 2014, nonostante Honda vinse 14 gare su 18 quell'anno."
                 " Questo perché nel biennio 2014-2015 venne introdotta nella classe MotoGP la sottocategoria Open, con moto più lente che correvano con le MotoGP"
                 " normali, alla quale Honda partecipò con un suo modello. Ovviamente le gare furono vinte dal team ufficiale dotato di Honda normali."
                 " Da notare inoltre il grandissimo step di Yamaha in termini di competitività dal 2007 al 2008, dove passò da essere tra le più lente ad essere la più veloce."
    )
    cons11.write("Infine notiamo come le velocità della classe MotoGP si riducono dal 2015 al 2016. Questo perché nel 2016 si passò da correre con gomme Bridgestone a gomme Michielin,"
                 " all'inizio meno competitive delle gomme precedenti. Ma non solo: nel 2016 si corsero più gare sul bagnato rispetto al 2015."
    )
    d_cons_filt_2=d_cons_speed.filter(pl.col("Constructor").is_in(cons_sel_2))
    c_year_list_2=sorted(d_cons_filt_2.select(pl.col("Year").unique()).to_series().to_list())
    st.session_state.c_year_list_2=c_year_list_2 #salvo un'altra lista di anni
    c_year_sel_2=cons11.slider("Inserire periodo da anlizzare:", min_value=c_year_list_2[0], max_value=max(c_year_list_2), value=(c_year_list_2[0], max(c_year_list_2)), key=8)
    d_cons_speed_year=d_cons_filt_2.filter(pl.col("Year")<=c_year_sel_2[1], pl.col("Year")>=c_year_sel_2[0])
    c_cat_list_2=sorted(d_cons_speed_year.select(pl.col("Cat").unique()).to_series().to_list())
    st.session_state.c_cat_list_2=c_cat_list_2 #salvo una lista di categorie
    c_cat_sel_2=cons11.multiselect("Inserire categoria desiderata:", c_cat_list_2, default=c_cat_list_2, key=12)
    if len(c_cat_sel_2)!=0:
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
        st.write("Per il confronto grafico selezionare almeno una categoria")
######### CAMBIAMO COMPLETAMENTE UNITA' STATISTICA #########
st.header("Analisi per piste")
st.subheader("Ohi, que calor!")
st.write("In questa sezione confronteremo le varie temperature medie di asfalto e aria per ogni pista, tenendo un minimo conto anche del periodo in cui si corre.")
data_track_temp=data.group_by("Year", pl.col("GP").alias("Track"), "Date","Track_Condition").agg(pl.col("Track_Temp").mean(), pl.col("Air_Temp").mean()).sort("Year","Track","Track_Condition",descending=False)
wet_dry=st.selectbox("Inserire condizione di pista desiderata", ["Dry", "Wet"])
st.write("Dry: Asciutto, Wet: Bagnato")
if wet_dry=="Dry":
    data_track_temp_d=data_track_temp.filter(pl.col("Track_Condition")=="Dry")
    trk1, trk2=st.columns(2)
    trk_list=sorted(data_track_temp_d.select("Track").unique().to_series().to_list())
    st.session_state.trk_list=trk_list #salvo la lista di tracciati
    trk_filt=trk1.multiselect("Selezionare pista/e d'interesse:", trk_list, default=trk_list[0])
    data_track_temp_d_filt=data_track_temp_d.filter(pl.col("Track").is_in(trk_filt))
    trk_year_list=sorted(data_track_temp_d_filt.select("Year").unique().to_series().to_list())
    st.session_state.trk_year_list=trk_year_list #salvo la lista di annate (dataset dei tracciati)
    year_filt=trk2.slider("Selezionare periodo d'interesse:", min_value=trk_year_list[0], max_value=max(trk_year_list), value=(trk_year_list[0], max(trk_year_list)),key=55)
    data_track_temp_d_final=data_track_temp_d_filt.filter(pl.col("Year")<=year_filt[1], pl.col("Year")>=year_filt[0])
    if len(trk_filt)==0:
        st.write("Selezionare almeno una pista")
    else:
        trk_chart_d_ttemp=alt.Chart(data_track_temp_d_final).mark_line().encode(
            alt.X("Year"), alt.Y("Track_Temp").scale(zero=False), alt.Color("Track"), alt.Text("Track_Temp"))
        trk_chart_d_atemp=alt.Chart(data_track_temp_d_final).mark_line().encode(
            alt.X("Year"), alt.Y("Air_Temp").scale(zero=False), alt.Color("Track"), alt.Text("Air_Temp"))
        st.write(data_track_temp_d_final)
        st.write("**Temperature asfalto**")
        st.altair_chart(trk_chart_d_ttemp, use_container_width=True)
        st.write("**Temperature aria**")
        st.altair_chart(trk_chart_d_atemp, use_container_width=True)
        st.write(data_track_temp_d_final)
else:
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
        st.write("Selezionare almeno una pista")
    else:
        trk_chart_d_ttemp=alt.Chart(data_track_temp_w_final).mark_line().encode(
            alt.X("Year"), alt.Y("Track_Temp").scale(zero=False), alt.Color("Track"), alt.Text("Track_Temp"))
        trk_chart_d_atemp=alt.Chart(data_track_temp_w_final).mark_line().encode(
            alt.X("Year"), alt.Y("Air_Temp").scale(zero=False), alt.Color("Track"), alt.Text("Air_Temp"))
        st.write(data_track_temp_w_final)
        st.write("**Temperature asfalto**")
        st.altair_chart(trk_chart_d_ttemp, use_container_width=True)
        st.write("**Temperature aria**")
        st.altair_chart(trk_chart_d_atemp, use_container_width=True)
##
st.subheader("Piste-aeroporti")
st.write(
    "In questa sezione confronteremo, come fatto già numerose volte in precedenza, le velocità medie. Questa volta, "
    "Ovviamente distingueremo tutto per categoria e condizioni della pista."
    )
data_trk_speed=data.group_by("Year",pl.col("GP").alias("Track"),"Category","Track_Condition").agg(pl.col("Avg_Speed").mean().alias("Speed"))
data_trk_speed=data_trk_speed.with_columns(
        pl.when(pl.col("Category").is_in(["125cc","Moto3"])).then(pl.lit("Lightweight")).otherwise(
            pl.when(pl.col("Category").is_in(["250cc","Moto2"])).then(pl.lit("Middleweight")).otherwise(pl.lit("MotoGP"))
        ).alias("Cat")
    ).select("Year", "Track","Cat","Track_Condition","Speed").drop_nulls()
wet_dry=st.selectbox("Inserire condizione di pista desiderata", ["Dry", "Wet"], key=69)
st.write("Dry: Asciutto, Wet: Bagnato")
if wet_dry=="Dry":
    d_t_speed_d=data_trk_speed.filter(pl.col("Track_Condition")=="Dry")
    trk_list_2=sorted(d_t_speed_d.select(pl.col("Track").unique()).to_series().to_list())
    st.session_state.trk_list_2=trk_list_2 #salvo la lista tracciati
    trk11, trk12=st.columns(2)
    trk_d_filt=trk11.multiselect("Inserire pista:", trk_list_2,default=trk_list_2[0],key=32)
    if len(trk_d_filt)==0:
        st.write("Inserire almeno una pista")
    else:
        d_t_speed_d_filt=d_t_speed_d.filter(pl.col("Track").is_in(trk_d_filt))
        t_year_list=sorted(d_t_speed_d_filt.select(pl.col("Year").unique()).to_series().to_list())
        st.session_state.t_year_list=t_year_list #salvo la lista anate (dataset tracciati)
        t_year_filt=trk11.slider("Inserire periodo desiderato:", min_value=t_year_list[0], max_value=max(t_year_list), value=(t_year_list[0], max(t_year_list)), key=42)
        d_t_speed_d_final=d_t_speed_d_filt.filter(pl.col("Year")<=t_year_filt[1], pl.col("Year")>=t_year_filt[0])
        st.write(d_t_speed_d_final.sort("Year", "Cat", descending=False))
        cat_trk_list=sorted(d_t_speed_d_final.select(pl.col("Cat").unique()).to_series().to_list())
        st.session_state.cat_trk_list=cat_trk_list #salvo la lista delle categorie (dataset tracciati)
        for i in cat_trk_list:
            d_t_speed_d_final_cat=d_t_speed_d_final.filter(pl.col("Cat")==str(i))
            t_speed_chart_d_cat=alt.Chart(d_t_speed_d_final_cat).mark_line().encode(
                alt.X("Year"), alt.Y("Speed").scale(zero=False), alt.Color("Track"), alt.Text("Speed")
                )
            st.write(str(i))
            st.altair_chart(t_speed_chart_d_cat, use_container_width=True)
else:
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
        d_t_speed_w_final=d_t_speed_w_filt.filter(pl.col("Year")<=t_year_filt[1], pl.col("Year")>=t_year_filt[0])
        st.write(d_t_speed_w_final.sort("Year", "Cat", descending=False))
        cat_trk_list=sorted(d_t_speed_w_final.select(pl.col("Cat").unique()).to_series().to_list())
        st.session_state.cat_trk_list=cat_trk_list #salvo la lista categorie (in base al dataset tracciati)
        for i in cat_trk_list:
            d_t_speed_w_final_cat=d_t_speed_w_final.filter(pl.col("Cat")==str(i))
            t_speed_chart_w_cat=alt.Chart(d_t_speed_w_final_cat).mark_line().encode(
                alt.X("Year"), alt.Y("Speed").scale(zero=False), alt.Color("Track"), alt.Text("Speed")
                )
            st.write(str(i))
            st.altair_chart(t_speed_chart_w_cat, use_container_width=True)
#####
st.title("SPERO SIA PIACIUTO COME PROGETTO, BUON PROSEGUIMENTO DI GIORNATA!")