# 🚀 Henry USA Dealer Scraper

A Python scraper that extracts dealer listings from the Henry USA directory and returns **only dealers with valid email addresses**.

---

## 🎯 Goal

Scrape the official Henry USA dealer directory:

🔗 https://www.henryusa.com/own-a-henry/find-a-henry-dealer/

Then **filter out all entries that do not include an email address**.

---

## 📊 Extracted Fields

- Dealer Name  
- Address  
- Phone  
- **Email (required filter)**  
- Website (if available)

---

## ⚙️ Features

- Parses unstructured HTML into clean structured data  
- Filters out non‑contactable dealers  
- Normalizes phone, email, and address formats  
- Exports results to Excel and CSV  

---

## 🔄 Pipeline

URL → Request → Parse HTML → Extract Data → Filter (email only) → Export
 
---

## 💡 Business Use Cases

- Lead generation  
- B2B outreach lists  
- Market research  
- Dealer network mapping  

---

## 📸 Demo

- Screenshot of the Henry USA dealer page
![Image Alt](https://github.com/angelsv27/directory-data-extractor/blob/934e86a3cf8066656348ff2ed528cf87d96c5f7e/assets/Dealers_in%20Alabama-Henry%20USA.JPG)
- Screenshot of the Excel output  
![Image Alt](https://github.com/angelsv27/directory-data-extractor/blob/934e86a3cf8066656348ff2ed528cf87d96c5f7e/assets/Specific_list_of%20Dealer%20Contacts%20US.JPG)
---

## 🧠 Tech Stack

- Python  
- BeautifulSoup / Scrapy  
- Pandas  

