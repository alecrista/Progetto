import streamlit as st
import altair as alt
import polars as pl
import datetime as dt
import pandas as pd
import math as mt
data=pl.read_csv("https://raw.githubusercontent.com/nbugliar/motogp_regression/master/MotoGP_2005_2017.csv", null_values=[" ","NA","crash"])
st.write("Nella colonna Position, dove manca il valore, è perché il pilota non ha terminato il Gran Premio.")
st.write("PURTROPPO, PER RAGIONI A NOI IGNOTE, NEL DATASET MANCANO I RISULTATI DEL GP DI SPAGNA CLASSE 125cc. LE CLASSIFICHE DI QUELLA STAGIONE RISULTAERANNO QUINDI ALTERATE.")
st.title("Database Motomondiale 2005-2017")
st.header("Database completo da analizzare")
st.write(data)
st.header("Classifiche generali")
col1, col2=st.columns(2)
year=col1.select_slider("Inserire anno:", range(2005,2018), key=1)
if year>2011:
    cat=col2.select_slider("Inserire Categoria:", ["MotoGP","Moto2","Moto3"])
elif (year>2009 and year<=2011):
    cat=col2.select_slider("Inserire Categoria:", ["MotoGP","Moto2","125cc"])
else:
    cat=col2.select_slider("Inserire Categoria:", ["MotoGP","250cc","125cc"])
# NEL GROUP BY TUTTE LE ALTRE COLONNE VANNO PERSE, PER CUI LE COLONNE DI FILTRAGGIO VANNO INSERITE.
col1.subheader("Classifica piloti")
col1.write(data.group_by("Year","Category","Rider_Name","Nationality").agg(pl.col("Points").sum(), pl.col("Bike").implode().list.unique())
         .filter(pl.col("Year")==year).filter(pl.col("Category")==cat).sort("Points", descending=True))
costr=data.group_by("Year", "TRK", "Category", "Bike").agg(pl.col("Points").max().alias("Tot_points")).sort("Year","Category","Bike", descending=True)
class_costr=costr.group_by("Year", "Category", "Bike").agg(pl.col("Tot_points").sum()).filter(pl.col("Year")==year, pl.col("Category")==cat).sort("Tot_points", descending=True)
col2.subheader("Classifica costruttori")
col2.write(class_costr)

########
st.header("Risultati di ogni GP per categoria")
year1=st.select_slider("Inserire anno:", range(2005,2018), key=2)
dataytd=data.select("Year","TRK","Date")
dataytd_filt=dataytd.filter(pl.col("Year")==year1).select("TRK", "Date")
pd_ytd=pd.DataFrame(dataytd_filt)
pd_ytd=pd_ytd.rename(columns={0:"TRK",1:"Date"})
datasort1=pd_ytd.drop_duplicates(subset="TRK").sort_values("Date")
trk=st.multiselect("Inserire GP:", datasort1["TRK"].to_list())
if str("USA") not in trk:
    for i in trk:
        col11, col12, col13=st.columns(3)
        d1=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category")=="MotoGP").filter(pl.col("Year")==year1).select(
        "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time","Year", "TRK", "Track")
        col11.write(d1)
        d2=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["250cc", "Moto2"])).filter(pl.col("Year")==year1).select(
        "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time","Year", "TRK", "Track")
        col12.write(d2)
        d3=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["125cc", "Moto3"])).filter(pl.col("Year")==year1).select(
        "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time","Year", "TRK", "Track")
        col13.write(d3)
else:
    d4=data.filter(pl.col("TRK").is_in(trk)).filter(pl.col("Category")=="MotoGP").filter(pl.col("Year")==year1).select(
        "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time","Year", "TRK", "Track")
    st.write(d4)
########
st.header("Analisi pilota per pilota")
st.subheader("Piloti e punti conquistati")
data_rider_points=data.group_by("Rider_Name","Year","Category","Bike").agg(pl.col("Points").sum()).sort("Rider_Name", "Year", descending=True)
rider_list=data_rider_points["Rider_Name"].unique().to_list()
cat_list=data_rider_points["Category"].unique().to_list()
col111, col112=st.columns(2)
riders=col111.multiselect("Inserire piloti desiderati:", rider_list)
category=col111.multiselect("Inserire Categoria desiderata:", cat_list)
col112.write(data_rider_points.filter(pl.col("Rider_Name").is_in(riders), pl.col("Category").is_in(category)))
st.subheader("Piloti e velocità dura e pura")
data_rider_speed=data.group_by("Rider_Name","Year","Category","Bike","Track_Condition").agg(
    pl.col("Avg_Speed").mean()).sort("Rider_Name", "Year", descending=True).filter(pl.col("Avg_Speed")>0) #Così rimuovo i dati assenti
st.write("*Pista asciutta*")
mud=data_rider_speed.filter(pl.col("Track_Condition")=="Dry").select(pl.col("Avg_Speed").mean())[0,0]#più conveniente di numpy
var=data_rider_speed.filter(pl.col("Track_Condition")=="Dry").select(pl.col("Avg_Speed").var())[0,0] #idem della riga 70
n=len(data_rider_speed.filter(pl.col("Track_Condition")=="Dry")["Rider_Name"].to_list())
st.write("Velocità media ti tutti i piloti:", mud)
ic=[mud-1.96*mt.sqrt(var*n/(n-1)), mud+1.96*mt.sqrt(var*n/(n-1))]
st.write("Intrvallo di confidenza a livello della velocità media, calcolato con l'opportuna formula mu +- 1.96 x sqrt(var x n/(n-1)):", ic)
st.write("Procedimento utilizzato per escludere valori poco significativi o poco rilevanti.")
st.write(data_rider_speed.filter(pl.col("Track_Condition")=="Dry").filter(pl.col("Avg_Speed")>=ic[0]).filter(pl.col("Avg_Speed")<=ic[1]))
st.write("*Pista bagnata*")
mud=data_rider_speed.filter(pl.col("Track_Condition")=="Wet").select(pl.col("Avg_Speed").mean())[0,0]#più conveniente di numpy
var=data_rider_speed.filter(pl.col("Track_Condition")=="Wet").select(pl.col("Avg_Speed").var())[0,0] #idem della riga 70
n=len(data_rider_speed.filter(pl.col("Track_Condition")=="Wet")["Rider_Name"].to_list())
st.write("Velocità media ti tutti i piloti:", mud)
ic=[mud-1.96*mt.sqrt(var*n/(n-1)), mud+1.96*mt.sqrt(var*n/(n-1))]
st.write("Intrvallo di confidenza a livello della velocità media, calcolato con l'opportuna formula mu +- 1.96 x sqrt(var x n/(n-1)):", ic)
st.write("Procedimento utilizzato per escludere valori poco significativi o poco rilevanti.")
st.write(data_rider_speed.filter(pl.col("Track_Condition")=="Wet").filter(pl.col("Avg_Speed")>=ic[0]).filter(pl.col("Avg_Speed")<=ic[1]))

######
st.header("Analisi per date")
col01, col02, col03=st.columns(3)
data_amg=st.date_input("Inserire data:", min_value=dt.date(2005, 1, 1), max_value=dt.date(2017, 12, 31))
data_date=data.with_columns(pl.col("Date").str.strptime(pl.Date, "%Y-%m-%d").alias("PyDate"))
st.write(data_date.filter(pl.col("PyDate")==data_amg))