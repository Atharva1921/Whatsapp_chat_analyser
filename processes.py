import re
import pandas as pd
from urlextract import URLExtract
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import seaborn as sns
from datetime import datetime

def preprocess(data):

    pattern = '\d{1,2}\/\d{1,2}\/\d{1,2},\s\d{1,2}:\d{2}\s-\s|\[\d{1,2}\/\d{1,2}\/\d{1,2}, \d{1,2}:\d{1,2}:\d{1,2}.[AaPp][Mm]\]'
    messages = re.split(pattern,data)[1:]
    dates = re.findall(pattern,data)
    dates = [ d.strip("[]") for d in dates]

    df = pd.DataFrame({'messages':messages,'dates':dates})
    date_string = dates[0]
    format_string = '%d/%m/%y, %I:%M:%S %p'

    try:
        res = bool(datetime.strptime(date_string, format_string))
    except Exception:
        res = False

    if res == True:
        df['dates'] = pd.to_datetime(df['dates'],format= '%d/%m/%y, %I:%M:%S %p')
    else:
        df['dates'] = pd.to_datetime(df['dates'],format= '%d/%m/%y, %H:%M - ')


    user = []
    message = []

    for m in messages:
        entry  = m.split(": ")
        if len(entry) == 2:
            user.append(entry[0])
            message.append(entry[1])
        else:
            user.append('group_notification')
            message.append(entry[0])

    df['user'] = user
    df['messages'] = message

    df['year'] = df['dates'].dt.year
    df['months'] = df['dates'].dt.month_name()
    df['day'] = df['dates'].dt.day
    df['hour'] = df['dates'].dt.hour
    df['minute'] = df['dates'].dt.minute
    df['month_num'] = df['dates'].dt.month
    df['day_name'] = df['dates'].dt.day_name()
    df['date'] = df['dates'].dt.date

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df

def fetch_stats(selected,df):

    if selected != 'Overall':
        df = df[df['user'] == selected]


    no_messages = df.shape[0]

    words = []
    for mes in df['messages']:
        words.extend(mes.split(" "))
    no_words = len(words)

    no_media = df[df['messages'] == '<Media omitted>\n'].shape[0]

    extractor = URLExtract()
    urls = []

    for mes in df['messages']:
        url = extractor.find_urls(mes)
        urls.extend(url)

    no_urls = len(urls)

    return no_messages,no_words,no_media, no_urls

def chat_contri(df):
    df_contri = round(df['user'].value_counts()/df.shape[0]*100,2).reset_index().rename(columns={'user':'name','count':'percent'})
    x = df['user'].value_counts().head()
    name = x.index
    count = x.values
    colors=['#00bf7d' , '#00b4c5' , '#0073e6' , '#2546f0' , '#5928ed', '#b3c7f7', '#8babf1', '#0073e6', '#0461cf',
            '#054fb9', '#c44601', '#f57600', '#8babf1', '#0073e6', '#5ba300', '#054fb9', '#89ce00', '#0073e6', '#e6308a', '#b51963']

    fig1, ax1 = plt.subplots()
    ax1.pie(count, labels=name,colors=colors, autopct='%1.1f%%',shadow=True, startangle=90)
    ax1.axis('equal')
    #chart = plt.pie(count,labels=name,autopct='%1.1f%%',shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9})

    return fig1 ,df_contri

def create_wordcloud(selected,df):

    f = open('stop_hinglish.txt','r')
    stopwords = f.read()
    f.close()

    if selected != 'Overall':
        df = df[df['user'] == selected]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['messages'] != '<Media omitted>\n']

    def remove_stopwords(message):
        y = []
        for word in message.lower().split():
            if word not in stopwords:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width = 800, height = 800,background_color ='white',
                    min_font_size = 10)
    temp['messages'].apply(remove_stopwords)
    wc_df = wc.generate(temp['messages'].str.cat(sep=" "))

    fig2,axis = plt.subplots()
    axis.imshow(wc_df)
    return fig2

def most_common_words(selected,df):

    f = open('stop_hinglish.txt','r')
    stopwords = f.read()
    f.close()

    if selected != 'Overall':
        df = df[df['user'] == selected]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['messages'] != '<Media omitted>\n']

    word_list = []
    for mes in temp['messages']:
        for word in mes.lower().split():
            if word not in stopwords:
                word_list.append(word)

    most_common_df = pd.DataFrame(Counter(word_list).most_common(20))

    fig3,axis = plt.subplots()
    axis.barh(most_common_df[0],most_common_df[1])
    plt.xticks(rotation= 'vertical')

    return fig3

def emoji(selected,df):
    import emoji
    if selected != 'Overall':
        df = df[df['user'] == selected]

    emojis = []
    for m in df['messages']:
        for c in m:
            if c in emoji.EMOJI_DATA:
                emojis.append(c)

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected,df):

    if selected != 'Overall':
        df = df[df['user'] == selected]

    monthly_timeline = df.groupby(['year','month_num','months']).count()['messages'].reset_index()
    time = []
    for i in range(monthly_timeline.shape[0]):
        time.append(monthly_timeline['months'][i] + "-" + str(monthly_timeline['year'][i]))
    monthly_timeline['time'] = time
    monthly_timeline = monthly_timeline[['messages','time']]

    return monthly_timeline

def daily_timeline(selected,df):

    if selected != 'Overall':
        df = df[df['user'] == selected]

    daily_timeline = df.groupby('date').count()['messages'].reset_index()

    fig4,axis = plt.subplots()
    axis.plot(daily_timeline['date'],daily_timeline['messages'], color='green')
    plt.xticks(rotation='vertical')

    return fig4

def Week_activity(selected,df):

    if selected != 'Overall':
        df = df[df['user'] == selected]  

    week_activity = df['dates'].dt.day_name().value_counts().reset_index()

    fig5,axis = plt.subplots()
    axis.bar(week_activity['dates'],week_activity['count'])
    plt.xticks(rotation= 'vertical')
    return fig5 

def Monthly_activity(selected,df):

    if selected != 'Overall':
        df = df[df['user'] == selected]  

    monthly_activity = df['months'].value_counts().reset_index()

    fig6,axis = plt.subplots()
    axis.bar(monthly_activity['months'],monthly_activity['count'],color='red')
    plt.xticks(rotation= 'vertical')
    return fig6 

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='messages', aggfunc='count').fillna(0)
    fig7,axis = plt.subplots()
    axis = sns.heatmap(user_heatmap)

    return fig7


