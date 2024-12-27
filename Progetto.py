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

#######
### CLASSIFICHE GENERALI ###
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
col1.write(data.group_by("Year","Category","Rider_Name","Nationality").agg(
    pl.col("Points").sum(), pl.col("Bike").implode().list.unique()).filter(pl.col("Year")==year).filter(
        pl.col("Category")==cat).sort("Points", descending=True))
costr=data.group_by("Year", "TRK", "Category", "Bike").agg(pl.col("Points").max().alias("Tot_points")).sort("Year","Category","Bike", descending=True)
class_costr=costr.group_by("Year", "Category", "Bike").agg(pl.col("Tot_points").sum()).filter(pl.col("Year")==year, pl.col("Category")==cat).sort("Tot_points", descending=True)
col2.subheader("Classifica costruttori")
col2.write(class_costr)

########
### CLASSIFICHE PER OGNI GP ###
st.header("Risultati di ogni GP per categoria")
mod=st.selectbox("Inserire modalità di filtraggio", ["Gran Premio - Anno", "Per data"])
if mod==str("Gran Premio - Anno"):
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
        col11.write(d1)
        d2=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["250cc", "Moto2"])).filter(pl.col("Year")==year1).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","Year", "TRK", "Track").sort("Position", descending=False)
        col12.write(d2)
        d3=data.filter(pl.col("TRK")==str(i)).filter(pl.col("Category").is_in(["125cc", "Moto3"])).filter(pl.col("Year")==year1).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","Year", "TRK", "Track").sort("Position", descending=False)
        col13.write(d3)
elif mod==str("Per data"):
    data_amg=st.date_input("Inserire data:", min_value=dt.date(2005, 1, 1), max_value=dt.date(2017, 12, 31))
    st.write("_*Selezionare una Domenica. In caso di tabelle vuote vuol dire che in quella data non è stato corso nessun gran premio.*_")
    data_date=data.with_columns(pl.col("Date").str.strptime(pl.Date, "%Y-%m-%d").alias("PyDate"))
    col11, col12, col13=st.columns(3)
    d1=data_date.filter(pl.col("PyDate")==data_amg).filter(pl.col("Category")=="MotoGP").filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","TRK","PyDate").sort("Position", descending=False)
    col11.write(d1)
    d2=data_date.filter(pl.col("PyDate")==data_amg).filter(pl.col("Category").is_in(["250cc", "Moto2"])).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","TRK","PyDate").sort("Position", descending=False)
    col12.write(d2)
    d3=data_date.filter(pl.col("PyDate")==data_amg).filter(pl.col("Category").is_in(["125cc", "Moto3"])).filter(pl.col("Position")>0).select(
            "Category", "Position", "Rider_Name", "Nationality", "Team_Name", "Bike","Time", "Points","TRK","PyDate").sort("Position", descending=False)
    col13.write(d3)
else:
    st.write("SELEZIONARE SOLO UNA DELLE 2 MODALITA'")

########
### ANALISI PER PILOTA ###
st.header("Analisi per pilota")
st.subheader("Piloti e punti conquistati")
st.write("Analisi effettuata sui piloti, non sulle categorie. Per cui selezionare prima il pilota e poi eventualmente la o le categorie")
data_rider_points=data.group_by("Rider_Name","Year","Category","Bike").agg(pl.col("Points").sum()).sort("Rider_Name", "Year", descending=True)
data_rider_points=data_rider_points.drop_nulls()
col111, col112=st.columns(2)
rider_list=sorted(data.select(pl.col("Rider_Name").unique()).drop_nulls().to_series().to_list())
riders=col111.multiselect("Inserire piloti desiderati:", rider_list)
d_filt_1=data_rider_points.filter(pl.col("Rider_Name").is_in(riders))
if len(riders)!=0:
    cat_list=sorted(d_filt_1.select(pl.col("Category").unique()).to_series().to_list())
    category=col112.multiselect("Inserire Categoria desiderata:", cat_list)
    d_filt_2=d_filt_1.filter(pl.col("Category").is_in(category))
    if len(category)!=0:
        year_list=sorted(d_filt_2.select(pl.col("Year").unique()).to_series().to_list())
        year=col112.select_slider("Inserire anno limite:", year_list)
        col111.write(d_filt_2.sort("Year", "Rider_Name", descending=True).filter(pl.col("Year")<=year))
        col112.altair_chart(
            alt.Chart(d_filt_2.filter(pl.col("Year")<=year)).mark_line().encode(alt.X("Year"), alt.Y("Points"), alt.Color("Rider_Name").scale(scheme="lightgreyred")),
            use_container_width=True
        )
    else:
        year_list=sorted(d_filt_1.select(pl.col("Year").unique()).to_series().to_list())
        year=col112.select_slider("Inserire anno limite:", year_list)
        col111.write(d_filt_1.sort("Year", "Rider_Name", descending=True).filter(pl.col("Year")<=year))
        col112.altair_chart(
            alt.Chart(d_filt_1.filter(pl.col("Year")<=year)).mark_line().encode(alt.X("Year"), alt.Y("Points"), alt.Color("Rider_Name").scale(scheme="lightgreyred")),
            use_container_width=True
        )
else:
    cat_list=sorted(data_rider_points.select(pl.col("Category").unique()).to_series().to_list())
    category=col112.multiselect("Inserire Categoria desiderata:", cat_list)
    d_filt_3=data_rider_points.filter(pl.col("Category").is_in(category))
    if len(category)!=0:
        year_list=sorted(d_filt_3.select(pl.col("Year").unique()).to_series().to_list())
        year=col112.select_slider("Inserire anno limite:", year_list)
        col111.write(d_filt_3.sort("Year", "Rider_Name", descending=True).filter(pl.col("Year")<=year))
        col112.altair_chart(
            alt.Chart(d_filt_3.filter(pl.col("Year")<=year)).mark_line().encode(alt.X("Year"), alt.Y("Points"), alt.Color("Rider_Name").scale(scheme="lightgreyred")),
            use_container_width=True
        )
    else:
        year_list=sorted(data_rider_points.select(pl.col("Year").unique()).to_series().to_list())
        year=col112.select_slider("Inserire anno limite:", year_list)
        col111.write(data_rider_points.sort("Year", "Rider_Name", descending=True).filter(pl.col("Year")<=year))
        col112.altair_chart(
            alt.Chart(data_rider_points.filter(pl.col("Year")<=year)).mark_line().encode(alt.X("Year"), alt.Y("Points"), alt.Color("Rider_Name").scale(scheme="lightgreyred")),
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
    .then(pl.lit("Lightweigth"))
    .otherwise(pl.when(pl.col("Category").is_in(["250cc","Moto2"]))
               .then(pl.lit("Middleweigth"))
               .otherwise(pl.lit("MotoGP")))
               .alias("Cat"))
dry1, dry2=st.columns(2)
dry1.write(d_dry_gen.sort("Year",descending=False).sort("Cat", descending=True))
chart_dry=alt.Chart(d_dry_gen).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed"), alt.Color("Cat").scale(scheme="viridis"))
dry2.altair_chart(chart_dry, use_container_width=False)
st.write("Svolgiamo un'analisi pilota per pilota.")
dry1, dry2=st.columns(2)
d_dry_rid=d_dry.group_by("Year","Category","Rider_Name","Bike").agg(pl.col("Avg_Speed").mean()).sort("Year","Category","Rider_Name", descending=False)
d_dry_rid=d_dry_rid.with_columns(
    pl.when(pl.col("Category").is_in(["125cc","Moto3"]))
    .then(pl.lit("Lightweigth"))
    .otherwise(pl.when(pl.col("Category").is_in(["250cc","Moto2"]))
               .then(pl.lit("Middleweigth"))
               .otherwise(pl.lit("MotoGP")))
               .alias("Cat"))
st.session_state.d_dry_rid=d_dry_rid
rid_dry=sorted(st.session_state.d_dry_rid.select("Rider_Name").unique().to_series().to_list())
rid_dry_sel=dry1.multiselect("Selezionare pilota desiderato", rid_dry)
if len(rid_dry_sel)==0:
    st.write("Inserire almeno un pilota")
else:
    data_dry_rid=d_dry_rid.filter(pl.col("Rider_Name").is_in(rid_dry_sel))
    st.session_state.data_dry_rid=data_dry_rid
    year_dry=sorted(st.session_state.data_dry_rid.select("Year").unique().to_series().to_list())
    year_dry_sel=dry1.select_slider("Selezionare anno desiderato", year_dry)
    data_dry_rid_year=data_dry_rid.filter(pl.col("Year")<=year_dry_sel)
    st.session_state.data_dry_rid_year=data_dry_rid_year
    cat_dry=sorted(st.session_state.data_dry_rid_year.select("Cat").unique().to_series().to_list())
    cat_dry_sel=dry1.multiselect("Selezionare categoria desiderata", cat_dry, default=cat_dry)
    data_dry_rid_year_cat=data_dry_rid_year.filter(pl.col("Cat").is_in(cat_dry_sel))
    dry2.write(data_dry_rid_year_cat)
    st.altair_chart(alt.Chart(data_dry_rid_year_cat).mark_line().encode(x="Year", y="Avg_Speed", color="Rider_Name"),
                use_container_width=True)
#
st.write("__*Pista bagnata*__")
muw=data_rider_speed.filter(pl.col("Track_Condition")=="Wet").select(pl.col("Avg_Speed").mean())[0,0]#più conveniente di numpy
st.write("Velocità media ti tutti i piloti:", muw)
d_wet=data_rider_speed.filter(pl.col("Track_Condition")=="Wet")
d_wet_gen=d_wet.group_by("Year","Category").agg(pl.col("Avg_Speed").mean()).sort("Year","Category", descending=False)
d_wet_gen=d_wet_gen.with_columns(
    pl.when(pl.col("Category").is_in(["125cc","Moto3"]))
    .then(pl.lit("Lightweigth"))
    .otherwise(pl.when(pl.col("Category").is_in(["250cc","Moto2"]))
               .then(pl.lit("Middleweigth"))
               .otherwise(pl.lit("MotoGP")))
               .alias("Cat"))
wet1,wet2=st.columns(2)
wet1.write(d_wet_gen.sort("Year",descending=False).sort("Cat", descending=True))
chart_wet=alt.Chart(d_wet_gen).mark_line().encode(alt.X("Year"), alt.Y("Avg_Speed"), alt.Color("Cat").scale(scheme="viridis"))
wet2.altair_chart(chart_wet, use_container_width=False)
st.write("Da notare che curiosamente, tra inizio 2012 e metà 2014, la classe leggera, probablimente perché ha corso meno gare e con un asfalto non completamente bagnato.")
##
st.subheader("Relazioni tra piloti e circuiti specifici")
st.write("*Piste orarie e antiorarie*")
data_o=data.filter(pl.col("r_corners")>pl.col("l_corners"))
data_a=data.filter(pl.col("r_corners")<pl.col("l_corners"))
st.write(data_o)
st.write(data_a)
st.write("*Piste spagnole*")
data_s=data.filter(pl.col("TRK").is_in(["SPA","VAL","ARA","CAT"]))
st.write(data_s)