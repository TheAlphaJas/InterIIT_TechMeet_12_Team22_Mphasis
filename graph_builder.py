import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# Read the dataset
def graph_builder(FlightSchedule,scoring_list,j,cancelled_list):
    df = FlightSchedule.copy()
    # new_df2 = new_df.drop('DepartureDates',axis=1)

    # final_df = pd.DataFrame()
    # print(len(FlightSchedule))

    # for i in range(len(list(new_df['ScheduleID']))):
    #     da = new_df.iloc[i]['DepartureDates'].strip('][').split(',')
    #     for j in range(len(da)):
    #         temdata = dict(new_df2.iloc[i])
    #         temdata['DepartureDates'] = da[j].strip(" ''")
    #         temdic = pd.DataFrame(temdata,index=[0])
    #         final_df = pd.concat([final_df,temdic])
    # final_df.reset_index(drop=True, inplace=True)
    # new_df3 = final_df
    # new_df3['ArvTime'] = np.NAN
    
    # new_df3['DepTime'] = pd.to_datetime(new_df3['DepartureTime']+ ' '+ new_df3['DepartureDates'])
    # for i in range(len(list(new_df3['ScheduleID']))):
    #     if pd.to_datetime(new_df3.iloc[i]['DepartureTime'])>pd.to_datetime(new_df3.iloc[i]['ArrivalTime']):
    #         new_df3.at[i,'ArvTime']  = pd.to_datetime(new_df3.iloc[i]['DepartureDates']+' '+new_df3.iloc[i]['ArrivalTime']) + pd.Timedelta(days=1)
    #     else:
    #         new_df3.at[i,'ArvTime']  = pd.to_datetime(new_df3.iloc[i]['DepartureDates']+' '+new_df3.iloc[i]['ArrivalTime'])
    print(len(df))
    for r in range(len(df)):
        try:
            df.at[r,'ArrivalAirport'] = df.iloc[r]['ArrivalAirport'].strip()
            df.at[r,'DepartureAirport'] = df.iloc[r]['DepartureAirport'].strip()
        except:
            print("KATA ",df.iloc[r]['ArrivalAirport'])
    for i in range(len(df)):
        if df.iloc[i]['ArrivalAirport'] != df.iloc[j]['ArrivalAirport']:
            df.at[i,'ArrivalDateTime'] = pd.to_datetime(df.at[i,'ArrivalDateTime']) + pd.Timedelta(hours=scoring_list[-1])
    df
    df.rename(columns={'DepartureAirport':'ORIG_CD','ArrivalAirport':'DEST_CD','ArrivalDateTime':'ARR_DTML','DepartureDateTime':'DEP_DTML'},inplace=True)
    
    # print(new_df)
    
    # Create a directed graph
    G = nx.DiGraph()
    df['ORIG_CD'] = (df['ORIG_CD'] + df['DEP_DTML'].astype(str))
    df['DEST_CD'] = (df['DEST_CD'] +  df['ARR_DTML'].astype(str))
    #print(df[['ORIG_CD','DEST_CD']].head(5))
    canc_start = df.loc[j, 'ORIG_CD']
    canc_dep = df.loc[j, 'DEST_CD']
    # Convert 'dept_time' and 'arr_time' to datetime if they are not already
    df['DEP_DTML'] = pd.to_datetime(df['DEP_DTML'])
    df['ARR_DTML'] = pd.to_datetime(df['ARR_DTML'])
    # Calculate the time difference between row 36 and each respective row
    df['departure_delay'] = df['DEP_DTML'] - df.loc[j, 'DEP_DTML']
    df['arrival_delay'] = df['ARR_DTML'] - df.loc[j, 'ARR_DTML']
    new_df = df.copy()
    df = df[abs(df['departure_delay']) <= pd.Timedelta(hours=(scoring_list[9]))]
    
    # Define a function to apply scoring rules
    def apply_scoring(row):
        score=0           
        if row['ORIG_CD'][:3] == canc_start[:3] and row['DEST_CD'][:3] != canc_dep[:3]:
            score += scoring_list[8]
        return score
    # Apply the scoring function to create the 'scores' column
    df['scores'] = df.apply(apply_scoring, axis=1)
    print("YAHAN DEKH\n", df.head())
    # Choose the columns you want to store in a list
    columns_to_store = ['ORIG_CD', 'DEST_CD']
    # Create a list of tuples, where each tuple contains the elements from the selected columns
    elements_list = list(zip(*[df[column] for column in columns_to_store]))
    flat_elements_list = [element for row in elements_list for element in row]
    flat_elements_list= sorted(flat_elements_list)
    for i, row in df.iterrows():
        G.add_node(row['ORIG_CD'])
        G.add_node(row['DEST_CD'])
        G.add_edge(row['ORIG_CD'], row['DEST_CD'], weight=row['scores'], FirstClass = row['FC_AvailableInventory'], BusinessClass=row['BC_AvailableInventory'], PremiumEconomyClass =row['PC_AvailableInventory'] ,EconomyClass =row['EC_AvailableInventory']  )
    def apply_scoring(time):
        if time is not pd.NaT:
            if pd.to_timedelta(time).total_seconds() / 3600 <= 6:
                score = scoring_list[0]
            elif pd.to_timedelta(time).total_seconds() / 3600 <= 12:
                score = scoring_list[1]
            elif pd.to_timedelta(time).total_seconds() / 3600 <= 24:
                score = scoring_list[2]
            elif pd.to_timedelta(time).total_seconds() / 3600 <= 48:
                score = scoring_list[3]
            else:
                score = 0  # Add this line to handle cases not covered by the previous conditions
            return score
        else:
            return 0
    #print("YAHAN DEKHO", canc_start, canc_dep)
    for i in range(1,len(flat_elements_list)):                    
            if (flat_elements_list[i][:3] == flat_elements_list[i-1][:3]) and (flat_elements_list[i][:3] != canc_start[:3]) and (flat_elements_list[i][:3] != canc_dep[:3]):
                G.add_edge(flat_elements_list[i-1], flat_elements_list[i], weight = 0)

                # if flat_elements_list[i] in df['ORIG_CD'].values and flat_elements_list[i-1] in df['ORIG_CD'].values:
                #     departure_delay = abs(df.loc[df['ORIG_CD'] == flat_elements_list[i], 'departure_delay'].iloc[0] - df.loc[df['ORIG_CD'] == flat_elements_list[i-1], 'departure_delay'].iloc[0])
                #     weight= apply_scoring(departure_delay)
                #     G.add_edge(flat_elements_list[i-1], flat_elements_list[i], weight=weight)
                # elif flat_elements_list[i] in df['DEST_CD'].values and flat_elements_list[i-1] in df['DEST_CD'].values:
                #     arrival_delay = abs(df.loc[df['DEST_CD'] == flat_elements_list[i], 'arrival_delay'].iloc[0] - df.loc[df['DEST_CD'] == flat_elements_list[i-1], 'arrival_delay'].iloc[0])
                #     weight= apply_scoring(arrival_delay)
                #     G.add_edge(flat_elements_list[i-1], flat_elements_list[i], weight=weight)
                # elif flat_elements_list[i] in df['DEST_CD'].values and flat_elements_list[i-1] in df['ORIG_CD'].values:
                #     delay = df.loc[df['DEST_CD'] == flat_elements_list[i], 'ARR_DTML'].iloc[0] - df.loc[df['ORIG_CD'] == flat_elements_list[i-1], 'DEP_DTML'].iloc[0]
                #     if delay.total_seconds() > 3600:
                #         weight = apply_scoring(delay)
                #         G.add_edge(flat_elements_list[i], flat_elements_list[i+1], weight=weight)
    print(flat_elements_list)
    for i in range(len(flat_elements_list)):
        if (flat_elements_list[i][:3] == canc_start[:3]) and (flat_elements_list[i] != canc_start):
           # print("BROO",flat_elements_list[i])
            #print(canc_start, flat_elements_list[i])
            #print(df.loc[df['DEST_CD'] == flat_elements_list[i], 'departure_delay'])
            if (len(df.loc[df['ORIG_CD'] == flat_elements_list[i], 'departure_delay'])==0):
                continue
            arrival_delay = abs(df.loc[df['ORIG_CD'] == canc_start, 'departure_delay'].iloc[0] - df.loc[df['ORIG_CD'] == flat_elements_list[i], 'departure_delay'].iloc[0])
            weight = apply_scoring(arrival_delay)
            G.add_edge(canc_start, flat_elements_list[i], weight=weight)
        elif (flat_elements_list[i][:3] == canc_dep[:3]) and (flat_elements_list[i] != canc_dep):
            if (len(df.loc[df['DEST_CD'] == flat_elements_list[i], 'arrival_delay'])==0):
                continue
            arrival_delay = abs(df.loc[df['DEST_CD'] == canc_dep, 'arrival_delay'].iloc[0] - df.loc[df['DEST_CD'] == flat_elements_list[i], 'arrival_delay'].iloc[0])
            weight = apply_scoring(arrival_delay)
            G.add_edge(flat_elements_list[i],canc_dep, weight=weight)
    print("HI")
    print(G.edges(data=True))
               # Plot the graph
    plt.figure(figsize=(10, 10))
    pos = nx.random_layout(G)  # You can use other layout algorithms as well
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='skyblue', font_color='black', font_size=10, edge_color='black', linewidths=1, alpha=0.7)
    # Add edge labels
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    #plt.figsi
    #print(df)
    # ze(100,100)
    l = list(new_df['ORIG_CD'])
    l2 = list(new_df['DEST_CD'])
    l3 = list(new_df['departure_delay'])
    print("pehle ",len(G.edges))
    print(len(df))
    #print(l)
    for j in cancelled_list:
        j = int(j)
        j-=2
        print(j)
        if abs(l3[j]) <= pd.Timedelta(hours=(scoring_list[9])):
            G.remove_edge(l[j], l2[j])
    print("ab ",len(G.edges))
    return G,l,l2
