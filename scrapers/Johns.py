from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import os
import time

# Place urls you want to scrape in list
urls = ['https://www.youtube.com/watch?v=YJym5QIC8aY']
# 'https://www.youtube.com/watch?v=YJym5QIC8aY'
# 'https://www.youtube.com/watch?v=8wFoXNJM2Is'
# 'https://www.youtube.com/watch?v=jVA-tr_euKU'
# 'https://www.youtube.com/watch?v=e8tyOzkJsMw'
# 'https://www.youtube.com/watch?v=Ai8Irb7L_JM'
# 'https://www.youtube.com/watch?v=1sxHoiW3jqo'
# 'https://www.youtube.com/watch?v=0bxIg3M_MHY'
# 'https://www.youtube.com/watch?v=HmZs6_CJ_u8'
# 'https://www.youtube.com/watch?v=27fQl4oRlBI'
# "https://www.youtube.com/watch?v=Xq-63bQP1BI"
# "https://www.youtube.com/watch?v=Efr9II6mS3I"
commentor_urls = []

location_from_urls = []

# Main function that scrapes comments from urls
def video_scrape(url):
    data_from_urls = []
    driver = webdriver.Chrome()
    driver.get(f"{url}")

    # The below function clicks on the 2 accept buttons which pop up when opening chrome from selenium
    def click_button(xpath):
        button = driver.find_element_by_xpath(xpath)
        driver.execute_script("arguments[0].click();", button)
    # While loops to click on buttons as fast as possible
    while True:
        try:
            click_button("/html/body/div/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/div[1]")
            break
        except:
            sleep(0.1)

    # while True:
    #     try:
    #         click_button("/html/body/ytd-app/ytd-popup-container/tp-yt-paper-dialog/yt-upsell-dialog-renderer/div/div[3]/div[1]/yt-button-renderer/a/tp-yt-paper-button/yt-formatted-string")
    #         break
    #     except:
    #         sleep(0.1)
    # Automated for loop to scroll to bottom of page (Note this is a set value so for very popular videos increase value in for loop)
    sleep(1.5)
    for num in range(2500):
        n = 40*num
        driver.execute_script(f"window.scrollTo(0, {n})")

    #  Using BeautifulSoup to scrape and print relevant information from comments
    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')
    title = soup.find('yt-formatted-string', {"class": "style-scope ytd-video-primary-info-renderer"}).text

    # title = "5 Habits That Made Me a Better Writer"
    path = f"{title}_1"
    os.mkdir(path)

    # Getting likes to dislikes is much harder than anticipated and requires more time to get hold of.

    # video_likes = soup.find('yt-formatted-string', class_="style-scope ytd-toggle-button-renderer style-text").text
    # print(video_likes)
    # video_dislikes = soup.find_all('div', id="top-level-buttons")
    # print(video_dislikes[0].text,video_dislikes[1].text,video_dislikes[2].text)

    like_bar = soup.find('div', id="like-bar").get("style")
    print(like_bar)

    comments = soup.find_all('div', {"id": "body"})
    print(len(comments))
    for info in comments:
        names = info.find('span', class_="style-scope ytd-comment-renderer").text.replace('              ', '')
        name_url = info.find('a', href=True)
        # Since some images don't save add them when you go to individual pages
        image = info.find('img', id='img').get('src')
        times = info.find('a', class_="yt-simple-endpoint style-scope yt-formatted-string").text
        comment = info.find('yt-formatted-string', id="content-text").text
        upvotes = info.find('span', id="vote-count-middle").text

        print(f'''
        ///
        Title: {title},
        Commentor name: {names}
        Time since posted: {times}
        Comment: {comment}
        Upvotes: {upvotes}
        Profile picture: {image}
        ///
        ''')
        ex = {
            "Commentor name": names,
            "Time since posted": times,
            "Comment": comment,
            "Upvotes": upvotes,
            "Profile Image": image
        }
        data_from_urls.append(ex)
        commentor_urls.append(name_url['href'])
        df = pd.DataFrame(data_from_urls)
        df.to_csv(os.path.join(path, f"Data from {title}.csv"))
    driver.quit()

    # for url in commentor_urls:
    #     data_from_videos = []
    #     driver = webdriver.Chrome()
    #     # Opens webdriver to persons videos
    #     driver.get(f"https://www.youtube.com{url}/videos")
    #
    #     while True:
    #         try:
    #             click_button("/html/body/div/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/div[2]")
    #
    #             break
    #         except:
    #             sleep(0.1)
    #
    #     sleep(2)
    #     content = driver.page_source
    #     soup = BeautifulSoup(content, 'lxml')
    #     channel_name = soup.find_all('ytd-channel-name', id='channel-name')
    #     list_for_name = []
    #     for name in channel_name:
    #         cha_name = name.find('yt-formatted-string', id='text').text
    #         list_for_name.append(cha_name)
    #     videos = soup.find_all('a', id='video-title')
    #     for video in videos:
    #         video_h = video['href']
    #
    #         ex = {
    #             "Channel videos": "https://www.youtube.com" + video_h,
    #         }
    #
    #         data_from_videos.append(ex)
    #         df = pd.DataFrame(data_from_videos)
    #         df.to_csv(os.path.join(path, f"Data from {title}, videos of {list_for_name[0]}.csv"))
    #
    #
    #     driver.quit()

    for url in commentor_urls:
        time1 = time.time
        data_from_videos = []
        driver = webdriver.Chrome()
        # Opens webdriver to persons related channels (there subscriptions)
        driver.get(f"https://www.youtube.com{url}/channels")

        while True:
            try:
                click_button("/html/body/div/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/div[2]")
                break
            except:
                sleep(0.1)

        # sleep(10)
        for num in range(2500):
            n = 50 * num
            driver.execute_script(f"window.scrollTo(0, {n})")

        content = driver.page_source
        soup = BeautifulSoup(content, 'lxml')
        channel_name = soup.find_all('ytd-channel-name', id='channel-name')
        list_for_name = []
        for name in channel_name:
            cha_name = name.find('yt-formatted-string', id='text').text
            list_for_name.append(cha_name)
        channels = soup.find_all('a', id='channel-info')
        for channel in channels:
            rel_channel = channel.text
            print(rel_channel)

            ex = {
                "Related channels": rel_channel,
            }

            data_from_videos.append(ex)
            df = pd.DataFrame(data_from_videos)
            df.to_csv(os.path.join(path, f"Data from {title}, related channels of {list_for_name[0]}.csv"))
    #
    #     # if(time.time() - time1 >= 30):
    #     #     driver.quit()


        driver.quit()

    # for url in commentor_urls:
    #     details_from_videos = []
    #     driver = webdriver.Chrome()
    #     # Opens webdriver to persons about page
    #     driver.get(f"https://www.youtube.com{url}/About")
    #
    #     while True:
    #         try:
    #             click_button("/html/body/div/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/div[2]")
    #             break
    #         except:
    #             sleep(0.1)
    #
    #     content = driver.page_source
    #     soup = BeautifulSoup(content, 'lxml')
    #     # Gets persons profile image
    #     img = soup.find('img', id='img').get('src')
    #     print(img)
    #     # This gets information on when they joined YouTube and there total channel views
    #     joined_and_views = soup.find('div', id="right-column")
    #     print(joined_and_views.text)
    #     # Copy's there channel description
    #     description = soup.find("yt-formatted-string", id='description')
    #     print(description.text)
    #     # Looks for and copy's there location
    #     details = soup.find_all('div', id='details-container')
    #     location_list_item = []
    #     for detail in details:
    #         location_list_item.append(detail.text)
    #     location_list_item = [i.replace('\n', '') for i in location_list_item]
    #     location_list_item = [i.replace('For business inquiries:Sign in to see email address', '') for i in location_list_item]
    #     location_list_item = [i.replace('Details', '') for i in location_list_item]
    #     print(location_list_item)
    #     # Grabs all there links
    #     links = soup.find_all('a', class_='yt-simple-endpoint style-scope ytd-channel-about-metadata-renderer')
    #     list_channel_links = []
    #     for link in links:
    #         list_channel_links.append(link['href'])
    #     channel_name = soup.find_all('ytd-channel-name', id='channel-name')
    #     list_for_name = []
    #     for name in channel_name:
    #         cha_name = name.find('yt-formatted-string', id='text').text
    #         list_for_name.append(cha_name)
    #
    #     ex = {
    #         "Channel name": list_for_name[0],
    #         "Profile image": img,
    #         "Day they joined youtube and views": joined_and_views.text,
    #         "Channel description": description.text,
    #         "Location": location_list_item[0],
    #         "Links": list_channel_links
    #     }
    #
    #     details_from_videos.append(ex)
    #     df = pd.DataFrame(details_from_videos)
    #     df.to_csv(os.path.join(path, f"Data from {title}, details of {list_for_name[0]}.csv"))
    #     sleep(2)
    #     driver.quit()


# For loop to iterate full process through urls in list
for url in urls:
    video_scrape(url)


print(commentor_urls)
print(location_from_urls)
