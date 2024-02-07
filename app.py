import streamlit as st
from io import StringIO
import processes


st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

    string_data = stringio.read()

    df = processes.preprocess(string_data)
    
    st.dataframe(df, use_container_width=True)

    user_list = df['user'].unique().tolist()
    user_list = list(filter(lambda x:x != 'group_notification',user_list))
    unique_users = user_list
    user_list.insert(0,"Overall")

    selected = st.sidebar.selectbox("show analysis with respect to:",user_list)
    if st.sidebar.button("Show analysis"):

        no_messages,no_words,no_media, no_urls = processes.fetch_stats(selected,df)

        col1, col2, col3,col4 = st.columns(4)


        with col1:
            st.header("Total Messages")
            st.title(no_messages)

        with col2:
            st.header("Total Words")
            st.title(no_words)

        with col3:
            st.header("Total Media")
            st.title(no_media)

        with col4:
            st.header("Total Links")
            st.title(no_urls)

        #Monthly timeline
        st.title("Monthly timeline:")
        monthly_timeline = processes.monthly_timeline(selected,df)
        st.line_chart(monthly_timeline, x=monthly_timeline.columns[1],y= monthly_timeline.columns[0])

        #Daily timeline
        st.title("Daily timeline:")
        daily_timeline = processes.daily_timeline(selected,df)
        st.pyplot(daily_timeline)

        col1, col2 = st.columns(2)

        with col1:
            #Week Activity
            st.title("Most busy days Weekly:")
            week_activity = processes.Week_activity(selected,df)
            st.pyplot(week_activity)

        with col2:
            #Monthly Activity
            st.title("Most busy days Monthly:")
            monthly_activity = processes.Monthly_activity(selected,df)
            st.pyplot(monthly_activity)



        if selected == 'Overall':
            st.title("Chat contribution:")
            
            chart, df_contri = processes.chat_contri(df)
            st.pyplot(chart)
            st.dataframe(df_contri, use_container_width=True)

        st.title("Word Cloud:")
        cloud_img = processes.create_wordcloud(selected,df)
        st.pyplot(cloud_img)

        st.title("Most common words:")
        most_common_graph = processes.most_common_words(selected,df)
        st.pyplot(most_common_graph)

        col1, col2 = st.columns(2)

        with col1:
            st.title("Most common Emojis:")
            emoji_df = processes.emoji(selected,df)
            st.dataframe(emoji_df,use_container_width=True)

        st.title("Weekly Activity Map")
        activity_heatmap = processes.activity_heatmap(selected,df)
        st.pyplot(activity_heatmap)

        
            