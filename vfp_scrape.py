import requests
from bs4 import BeautifulSoup
import time
import json
import csv

BASE_URL = "https://www.tek-tips.com/forums/microsoft-foxpro.184/"

# Function to fetch and parse a page
def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful
    return BeautifulSoup(response.content, 'html.parser')

def extract_threads(main_page_url, max_pages = 3): #added max_pages for testing purposes
    threads_data = []
    current_page_url = main_page_url
    page_count = 0 #for testing purposes

    while current_page_url and page_count < max_pages: #adding the < for testing pruposes
        soup = fetch_page(current_page_url)
        
        # Find all thread containers
        thread_containers = soup.find_all('div', class_='structItem-cell structItem-cell--main')
        
        for thread_container in thread_containers:
            # Extract title
            title_tag = thread_container.find('div', class_='structItem-title').find('a')
            if not title_tag:
                continue  # Skip if title not found
            
            title = title_tag.get_text(strip=True)
            link = "https://www.tek-tips.com" + title_tag['href']
    
            # Extract author
            minor_section = thread_container.find('div', class_='structItem-minor')
            author_tag = minor_section.find('a', class_='username') if minor_section else None
            author = author_tag.get_text(strip=True) if author_tag else "Unknown"
    
            # Extract timestamp
            time_tag = minor_section.find('time') if minor_section else None
            timestamp = time_tag['title'] if time_tag else "No timestamp"
    
            # Store the thread details
            threads_data.append({
                'title': title,
                'author': author,
                'timestamp': timestamp,
                'link': link
            })
        
        # Find the "Next" button and get the URL for the next page
        next_button = soup.find('a', class_='pageNav-jump pageNav-jump--next')
        if next_button:
            current_page_url = "https://www.tek-tips.com" + next_button['href']
            print(f"Moving to next page: {current_page_url}")
        else:
            current_page_url = None  # No "Next" button means we reached the last page

        time.sleep(1)  # To avoid making too many requests quickly

        page_count += 1 #for  testing purposes
        
    return threads_data

# Function to scrape replies for a thread
def scrape_replies(thread_url):
    soup = fetch_page(thread_url)
    
    replies = soup.find_all('article', class_='message')  # Ensure correct selector
    
    replies_data = []
    
    for index, reply in enumerate(replies):
        # Extract author
        author_tag = reply.find('a', class_='username')
        reply_author = author_tag.get_text(strip=True) if author_tag else "Unknown"
        
        # Extract message
        message_tag = reply.find('div', class_='bbWrapper')
        reply_message = message_tag.get_text(strip=True) if message_tag else "No message"

        # Extract timestamp: Date from data-date-string, Time from title
        time_tag = reply.find('time', class_='u-dt')
        if time_tag and 'data-date-string' in time_tag.attrs and 'title' in time_tag.attrs:
            date = time_tag['data-date-string']
            time = time_tag['title']
            timestamp = f"{date} at {time}"
        else:
            timestamp = "No timestamp"

        # Determine if it's the first post (question) or a reply
        post_type = "Question" if index == 0 else "Reply"

        replies_data.append({
            'post_type': post_type,
            'author': reply_author,
            'timestamp': timestamp,
            'message': reply_message
        })
    
    return replies_data

# Function to export the scraped threads and replies to a JSON file
def export_to_json(threads_data, filename="threads_data.json"):
    formatted_data = []
    
    for thread in threads_data:
        formatted_thread = {
            "question": {
                "title": thread["title"],
                "author": thread["author"],
                "timestamp": thread["timestamp"],
                "link": thread["link"],
                "message": thread["replies"][0]["message"] if thread["replies"] else "No content"
            },
            "replies": thread["replies"][1:]  # Exclude the first post since it's the question
        }
        formatted_data.append(formatted_thread)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)

# Function to export the scraped threads and replies to a CSV file
def export_to_csv(threads_data, filename="threads_data.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['Post Type', 'Title', 'Author', 'Timestamp', 'Thread Link', 'Reply Author', 'Reply Message'])
        
        for thread in threads_data:
            # Write the first post as the question
            first_post = thread['replies'][0] if thread['replies'] else {"message": "No content", "author": thread['author']}
            writer.writerow(["Question", thread['title'], thread['author'], thread['timestamp'], thread['link'], first_post["author"], first_post["message"]])
            
            # Write replies under the question
            for reply in thread['replies'][1:]:
                writer.writerow(["Reply", thread['title'], thread['author'], thread['timestamp'], thread['link'], reply['author'], reply['message']])

# Main function to execute the scraper
def main():
    print("Scraping the main page for threads...")
    threads = extract_threads(BASE_URL)
    
    threads_data = []
    
    for thread in threads[:]:
        thread_data = {
            'title': thread['title'],
            'author': thread['author'],
            'timestamp': thread['timestamp'],
            'link': thread['link'],
            'replies': []
        }

        # Scrape replies for each thread
        print(f"Scraping replies for {thread['title']}...")
        replies = scrape_replies(thread['link'])
        thread_data['replies'] = replies

        threads_data.append(thread_data)
        
        time.sleep(1)  # To avoid making too many requests quickly

    # Export the data to JSON and CSV files
    export_to_json(threads_data)
    print(f"Data exported to threads_data.json")
    
    export_to_csv(threads_data)
    print(f"Data exported to threads_data.csv")

if __name__ == "__main__":
    main()



# import requests
# from bs4 import BeautifulSoup
# import time
# import json
# import csv

# # Base URL of the Tek-Tips FoxPro forum
# BASE_URL = "https://www.tek-tips.com/forums/microsoft-foxpro.184/"

# # Function to fetch and parse a page
# def fetch_page(url):
#     response = requests.get(url)
#     response.raise_for_status()  # Check if the request was successful
#     return BeautifulSoup(response.content, 'html.parser')

# def extract_threads(main_page_url):
#     soup = fetch_page(main_page_url)
    
#     # Find all thread containers
#     thread_containers = soup.find_all('div', class_='structItem-cell structItem-cell--main')
    
#     thread_details = []
    
#     for thread_container in thread_containers:
#         # Extract title
#         title_tag = thread_container.find('div', class_='structItem-title').find('a')
#         if not title_tag:
#             continue  # Skip if title not found
        
#         title = title_tag.get_text(strip=True)
#         link = "https://www.tek-tips.com" + title_tag['href']

#         # Extract author
#         minor_section = thread_container.find('div', class_='structItem-minor')
#         author_tag = minor_section.find('a', class_='username') if minor_section else None
#         author = author_tag.get_text(strip=True) if author_tag else "Unknown"

#         # Extract timestamp
#         time_tag = minor_section.find('time') if minor_section else None
#         timestamp = time_tag['title'] if time_tag else "No timestamp"

#         # Store the thread details
#         thread_details.append({
#             'title': title,
#             'author': author,
#             'timestamp': timestamp,
#             'link': link
#         })

#     return thread_details

# # Function to scrape replies for a thread
# def scrape_replies(thread_url):
#     soup = fetch_page(thread_url)
    
#     replies = soup.find_all('article', class_='message')  # Ensure correct selector
    
#     replies_data = []
    
#     for index, reply in enumerate(replies):
#         # Extract author
#         author_tag = reply.find('a', class_='username')
#         reply_author = author_tag.get_text(strip=True) if author_tag else "Unknown"
        
#         # Extract message
#         message_tag = reply.find('div', class_='bbWrapper')
#         reply_message = message_tag.get_text(strip=True) if message_tag else "No message"

#         # Extract timestamp: Date from data-date-string, Time from title
#         time_tag = reply.find('time', class_='u-dt')
#         print('TIMETAG: ', time_tag)
#         if time_tag and 'data-date-string' in time_tag.attrs and 'title' in time_tag.attrs:
#             date = time_tag['data-date-string']
#             time = time_tag['title']
#             timestamp = f"{date} at {time}"
#         else:
#             timestamp = "No timestamp"

#         print('TIMESTAMPJ: ', timestamp)

#         # Determine if it's the first post (question) or a reply
#         post_type = "Question" if index == 0 else "Reply"

#         replies_data.append({
#             'post_type': post_type,
#             'author': reply_author,
#             'timestamp': timestamp,
#             'message': reply_message
#         })
    
#     return replies_data

# # Function to export the scraped threads and replies to a JSON file
# def export_to_json(threads_data, filename="threads_data.json"):
#     formatted_data = []
    
#     for thread in threads_data:
#         formatted_thread = {
#             "question": {
#                 "title": thread["title"],
#                 "author": thread["author"],
#                 "timestamp": thread["timestamp"],
#                 "link": thread["link"],
#                 "message": thread["replies"][0]["message"] if thread["replies"] else "No content"
#             },
#             "replies": thread["replies"][1:]  # Exclude the first post since it's the question
#         }
#         formatted_data.append(formatted_thread)
    
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(formatted_data, f, ensure_ascii=False, indent=4)

# # Function to export the scraped threads and replies to a CSV file
# def export_to_csv(threads_data, filename="threads_data.csv"):
#     with open(filename, 'w', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         # Write header
#         writer.writerow(['Post Type', 'Title', 'Author', 'Timestamp', 'Thread Link', 'Reply Author', 'Reply Message'])
        
#         for thread in threads_data:
#             # Write the first post as the question
#             first_post = thread['replies'][0] if thread['replies'] else {"message": "No content", "author": thread['author']}
#             writer.writerow(["Question", thread['title'], thread['author'], thread['timestamp'], thread['link'], first_post["author"], first_post["message"]])
            
#             # Write replies under the question
#             for reply in thread['replies'][1:]:
#                 writer.writerow(["Reply", thread['title'], thread['author'], thread['timestamp'], thread['link'], reply['author'], reply['message']])

# # Main function to execute the scraper
# def main():
#     print("Scraping the main page for threads...")
#     threads = extract_threads(BASE_URL)
    
#     threads_data = []
    
#     for thread in threads[:5]:  # Limiting to 5 threads for testing
#         thread_data = {
#             'title': thread['title'],
#             'author': thread['author'],
#             'timestamp': thread['timestamp'],
#             'link': thread['link'],
#             'replies': []
#         }

#         # Scrape replies for each thread
#         print(f"Scraping replies for {thread['title']}...")
#         replies = scrape_replies(thread['link'])
#         thread_data['replies'] = replies

#         threads_data.append(thread_data)
        
#         time.sleep(1)  # To avoid making too many requests quickly

#     # Export the data to JSON and CSV files
#     export_to_json(threads_data)
#     print(f"Data exported to threads_data.json")
    
#     export_to_csv(threads_data)
#     print(f"Data exported to threads_data.csv")

# if __name__ == "__main__":
#     main()
