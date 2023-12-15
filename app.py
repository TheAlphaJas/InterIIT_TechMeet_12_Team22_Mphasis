import streamlit as st
import pandas as pd
import networkx as nx
from io import StringIO
from graph_builder import graph_builder
from bbx import bbx
from qaoa_optimizer import draw_graph

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True) 

st.title('Inter IIT Tech Meet 12: Quantum C.')

#File upload 
st.markdown("<p class='first'>Upload the Flight Schedule</p>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(" ",type='csv')
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    # st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    FlightSchedule = pd.read_csv(uploaded_file)
    st.write(FlightSchedule)

# Add padding with Markdown
st.markdown("<br>", unsafe_allow_html=True)

#File upload 
st.markdown("<p class='second'>Upload the Cancelled Flights Data</p>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("",type = 'csv')
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    # st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    CancelledFlights = pd.read_csv(uploaded_file)
    st.write(CancelledFlights)

# Add padding with Markdown
st.markdown("<br>", unsafe_allow_html=True)

#File upload 
st.markdown("<p class='third'>Upload the PNR Data</p>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("        ",type = 'csv')
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    # st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    # st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    PNRData = pd.read_csv(uploaded_file)
    st.write(PNRData)

#### RULESET ####
st.markdown("---")
st.markdown("<p class='ruleset'> Customize your Rules Here </p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


#Form
with st.form("my_form"):
   st.markdown("<h3>Alternate Flight Ranking Rules</h3>", unsafe_allow_html=True)
   scoring_list=[]
   pnr_scoring_list = []
   with st.expander("Detailed Flight Scoring"):
   #arrival
    st.markdown("<p class='form_head'>Arrival Delay</p>", unsafe_allow_html=True)
    a6 = st.number_input('Arrival Delay <= 6 hours',value = 70.00)
    scoring_list.append(a6)
    a12 = st.number_input('Arrival Delay <= 12 hours',value = 50.00)
    scoring_list.append(a12)
    a24 = st.number_input('Arrival Delay <= 24 hours',value = 40.00)
    scoring_list.append(a24)
    a48 = st.number_input('Arrival Delay <= 48 hours',value = 30.00)
    scoring_list.append(a48)
   #departure
    st.markdown("<p class='form_head'>STD of proposed flight</p>", unsafe_allow_html=True)
    d6 = st.number_input('SPF <= 6 hours of original',value = 70.00)
    scoring_list.append(d6)
    d12 = st.number_input('SPF <= 12 hours of original',value = 50.00)
    scoring_list.append(d12)
    d24 = st.number_input('SPF <= 24 hours of original',value = 40.00)
    scoring_list.append(d24)
    d48 = st.number_input('SPF <= 48 hours of original',value = 30.00)
    scoring_list.append(d48)
    tx1 = st.number_input("Maximum Delay of departure time in hours",value = 24.00) 
   #Stop over
    st.markdown("<p class='form_head'>Stop over</p>", unsafe_allow_html=True)
    so = st.number_input('Stop over scoring',value = -20.00)
    scoring_list.append(so)
    scoring_list.append(tx1)
   # PNR Ranking
   st.markdown("<h3>PNR Ranking Criteria</h3>", unsafe_allow_html=True)
   with st.expander("Detailed PNR Scoring"):
    st.markdown("<p class='form_head'>Seating Cabin</p>", unsafe_allow_html=True)
   #CABIN SCORES
    first_class_score = st.number_input('First Class Score',value = 2000.00)
    business_class_score = st.number_input('Business Class Score',value = 1800.00)
    premium_economy_score = st.number_input('Premium Economy Score',value = 1600.00)
    economy_score = st.number_input('Economy Score',value = 1500.00)
    st.markdown("<p class='form_head'>Loyalty</p>", unsafe_allow_html=True)
   #LOYALTY SCORES
    presidential_platinum_score = st.number_input('Presidential Platinum Loyalty Score',value = 2000.00)
    platinum_score = st.number_input('Platinum Loyalty Score',value = 1800.00)
    gold_score = st.number_input('Gold Loyalty Score',value = 1600.00)
    silver_score = st.number_input('Silver Loyalty Score',value = 1500.00)
    st.markdown("<p class='form_head'>General</p>", unsafe_allow_html=True)
   #GENERAL SCORES
    ssr_score = st.number_input('SSR Score',value = 200.00)
    downline_connection_score = st.number_input('Per Downline Connection Score',value = 100.00)
    booking_type_score = st.number_input('Booking Type(Corp,Group etc.) Score',value = 500.00)
    score_per_passenger = st.number_input('Score Per Passenger', value = 50.00)
    pnr_scoring_list.extend([ssr_score,first_class_score,business_class_score,premium_economy_score,economy_score,downline_connection_score,booking_type_score,score_per_passenger,presidential_platinum_score,platinum_score,gold_score,silver_score])
   submitted = st.form_submit_button("Submit")
   if submitted:
        # G = nx.DiGraph()
        # G.add_edge(1,0,weight=4)
        # G.add_edge(1,4,weight=4)
        G=graph_builder(FlightSchedule,scoring_list,1)
        # G = nx.DiGraph()
        # G.add_edge("hi","yes",weight = 5)
        # G.add_edge("skip","no",weight = 5)
        print("EDGES ",G.edges(data=True))
        #draw_graph(G)
        G = bbx(G,2,5)
        print(G.edges(data=True))
        #print(G)
        st.pyplot(draw_graph(G))