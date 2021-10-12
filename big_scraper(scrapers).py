import sqlite3
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from textblob import TextBlob
import pandas as pd
from mysql import add_to_db

def scrape(driver, game_id, conn, options):
    # Scroll down the comments to load them. If the 'see more content' button appears click it.
    for num in range(100):
        n = 40 * num
        driver.execute_script(f"window.scrollTo(0, {n})")
        if num % 100 == 0:
            try:
                more_content_btn = driver.find_element_by_link_text("See More Content")
                driver.execute_script("arguments[0].click();", more_content_btn)
            except:
                continue

    # Get the html code
    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')
    # List of dictionaries. Each dictionary has information about one comment
    comments = []
    comment_cards = soup.find_all('div', {"class": "apphub_Card modalContentLink interactable"})
    # back_to_top_btn = driver.find_element_by_link_text("Back to top")
    # driver.execute_script("arguments[0].click();", back_to_top_btn)
    errors = 0
    for i in range(len(comment_cards)):
        '''
        if i % 50 == 0:
            for num in range(1000):
                n = 40 * num
                driver.execute_script(f"window.scrollBy(0, window.scrollY + {n})")
                if num % 100 == 0:
                    try:
                        more_content_btn = driver.find_element_by_link_text("See More Content")
                        driver.execute_script("arguments[0].click();", more_content_btn)
                    except:
                        continue
        '''
        comment_info = {
            "comment": "",
            "num_found_helpful": "",
            "suggestion": "",
            "date": "",
            "sentiment": 0,
            "commenter_name": "",
            "commenter_nickname": "",
            "location": "",
            "level": "",
            "hours_played": "",
            "game_name": "",
            "users_comments": []
        }

        found_helpful = comment_cards[i].find('div', {"class": "found_helpful"})
        if found_helpful is not None:
            found_helpful = found_helpful.text.split()
            num_found_helpful = found_helpful[0]
        else:
            num_found_helpful = 0
        suggestion = comment_cards[i].find('div', {"class": "title"}).text
        comment = comment_cards[i].find('div', {"class": "apphub_CardTextContent"}).text
        comment = comment.split("\n")
        date = comment[1].replace("Posted: ", "").replace('"', "")
        comment = comment[2].replace("\t", "")
        # Get the sentiment of the comment
        comment = TextBlob(comment)
        sentiment = comment.sentiment.polarity

        commenter_name = comment_cards[i].find('div', {"class": "apphub_CardContentAuthorBlock tall"}).text
        commenter_name = commenter_name.strip()
        commenter_name = commenter_name.split("\n")
        commenter_name = commenter_name[0]

        # time.sleep(3)
        # Get the link to the commenter's profile and open it in a new browser.
        try:
            user_href = comment_cards[i].find('a', href=True)
        except:
            print("Could not find:", commenter_name)
            errors += 1
            # try:
            # cancel_button = driver.find_element_by_link_text("Cancel")
            # driver.execute_script("arguments[0].click();", cancel_button)
            # except:
            # errors = errors
            for num in range(500):
                n = 40 * num * i
                driver.execute_script(f"window.scrollTo(0, window.scrollY + {n})")
                if num % 100 == 0:
                    try:
                        more_content_btn = driver.find_element_by_link_text("See More Content")
                        driver.execute_script("arguments[0].click();", more_content_btn)
                    except:
                        continue
            continue

        driver_3 = webdriver.Chrome(options=options)
        driver_3.get(user_href['href'])

        user_content = driver_3.page_source
        user_soup = BeautifulSoup(user_content, 'lxml')
        try:
            try:
                hours_played = user_soup.find('div', {"class": "value"}).text
            except:
                hours_played = ""
            level = user_soup.find('span', {"class": "friendPlayerLevelNum"}).text
        except:
            hours_played = ""
            level = ""
        try:
            nickname_and_location = user_soup.find('div', {"class": "header_real_name ellipsis"})
            nickname = nickname_and_location.bdi.text
            try:
                nickname_and_location = nickname_and_location.text
                nickname_and_location = nickname_and_location.strip().replace("\t", "").replace("\n\n", "")
                location = nickname_and_location.split("\n")[1].replace("\xa0", "")
            except:
                location = ""
        except:
            nickname = ""
            location = ""

        try:
            user_reviews_button = driver_3.find_element_by_partial_link_text("Reviews")
            driver_3.execute_script("arguments[0].click();", user_reviews_button)
            user_reviews_content = driver_3.page_source
            user_reviews_soup = BeautifulSoup(user_reviews_content, 'lxml')
            user_comment_cards = user_reviews_soup.find_all('div', {"class": "review_box"})
            users_comments = []
            for card in user_comment_cards:
                users_comment = card.find('div', {"class": "content"}).text.replace("\t", "")
                users_comments.append(users_comment)
            driver_3.quit()
        except:
            driver_3.quit()
            users_comments = "N/A"

        comment_info["comment"] = comment
        comment_info["num_found_helpful"] = num_found_helpful
        comment_info["suggestion"] = suggestion
        comment_info["date"] = date
        comment_info["sentiment"] = sentiment
        comment_info["users_comments"] = users_comments
        comment_info["commenter_name"] = commenter_name
        comment_info["commenter_nickname"] = nickname
        comment_info["location"] = location
        comment_info["level"] = level
        comment_info["hours_played"] = hours_played
        comment_info["game_name"] = game_id
        comments.append(comment_info)

        conn.execute("INSERT INTO COMMENTERS VALUES (?,?,?,?,?,?)",
                     (commenter_name, game_id, nickname, location, level, hours_played))
        conn.commit()

        # print(comment_info)
    df = pd.DataFrame(comments)
    df.to_csv('comments_db.csv', mode='a', header=False)
    driver.quit()
    print("errors:", errors)
    return comments

def main():
    conn = sqlite3.connect('scraperdb.db')

    conn.execute('''CREATE TABLE GAMES
    (GAME_ID TEXT PRIMARY KEY,
    GAME_DESCRIPTION TEXT,
    GAME_LINK TEXT);''')

    conn.execute('''CREATE TABLE COMMENTERS
    (COMMENTER_ID TEXT PRIMARY KEY,
    GAME_ID TEXT,
    COMMENTER_REAL_NAME TEXT,
    LOCATION TEXT,
    LEVEL TEXT,
    HOURS PLAYED TEXT);''')

    url = 'https://store.steampowered.com/search/?sort_by=_ASC&os=win&filter=topsellers'
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.get(f"{url}")

    time.sleep(1.5)
    for num in range(500):
        n = 40 * num
        driver.execute_script(f"window.scrollTo(0, {n})")

    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')
    game_names = soup.find_all('span', {"class": "title"})
    #game_links = soup.find_all('a', {"class": "search_result_row ds_collapse_flag  app_impression_tracked"}, href=True)
    # mature_game = False
    for i in range(10):
        games_buttons = driver.find_elements_by_css_selector("a[class='search_result_row ds_collapse_flag ']")
        driver.execute_script("arguments[0].click();", games_buttons[i])
        game_link = driver.current_url
        game_name = game_names[i].text
        driver.back()
        driver2 = webdriver.Chrome(options=options)
        driver2.get(game_link)

        try:
            driver2.find_element_by_xpath('//*[@id="ageYear"]/option[101]').click()
            view_page = driver2.find_element_by_xpath('//*[@id="app_agegate"]/div[1]/div[4]/a[1]/span')
            driver2.execute_script("arguments[0].click();", view_page)
            # mature_game = True
        except:
            pass

        content2 = driver2.page_source
        soup2 = BeautifulSoup(content2, 'lxml')
        try:
            game_description = soup2.find('div', {"class": "game_area_description"}).text
        except:
            game_description = ""

        try:
            for num in range(500):
                n = 40 * num
                driver2.execute_script(f"window.scrollTo(0, {n})")
            see_all_button = driver2.find_element_by_xpath('//*[@id="ViewAllReviewssummary"]/a')
            driver2.execute_script("arguments[0].click();", see_all_button)
            try:
                mature_view = driver2.find_element_by_xpath('//*[@id="age_gate_btn_continue"]/span')
                driver2.execute_script("arguments[0].click();", mature_view)
            except:
                pass
            conn.execute("INSERT INTO GAMES VALUES (?,?,?)", (game_name, game_description, game_link))
            conn.commit()
            scrape(driver2, game_name, conn, options)
            driver2.back()
        except:
            pass
            # try:
            #     time.sleep(1)
            #     content = driver.page_source
            #     soup = BeautifulSoup(content, 'lxml')
            #     hallo = soup.find_all('div', {"class": "vote_info"})
            #     scrape(driver)
            # except:
            #     pass

        #driver.back()
        driver2.quit()
        # if mature_game:
        #     driver.back()
        #     mature_game = False
    driver.quit()
    conn.close()


if __name__ == '__main__':
    main()
