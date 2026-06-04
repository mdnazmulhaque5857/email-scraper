import re
import streamlit as st
import requests
from bs4 import BeautifulSoup

# Define a robust regex pattern for email matching
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

def extract_emails_from_url(url):
    """Fetches a URL and extracts unique emails from text and mailto links."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    emails = set()
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            text_emails = re.findall(EMAIL_REGEX, html_content)
            for email in text_emails:
                emails.add(email.lower().strip())
                
            soup = BeautifulSoup(html_content, 'html.parser')
            for anchor in soup.find_all('a', href=True):
                href = anchor['href']
                if href.startswith('mailto:'):
                    clean_email = href.replace('mailto:', '').split('?')[0].strip()
                    if re.match(EMAIL_REGEX, clean_email):
                        emails.add(clean_email.lower())
                        
            return list(emails), "Success"
        else:
            return [], f"Error: Status Code {response.status_code}"
    except requests.exceptions.Timeout:
        return [], "Error: Connection Timeout"
    except requests.exceptions.ConnectionError:
        return [], "Error: Failed to connect"
    except Exception as e:
        return [], f"Error: {str(e)}"

# --- STREAMLIT UI ---
st.set_page_config(page_title="Bulk Email Extractor", page_icon="✉️", layout="wide")

st.title("✉️ Bulk Website Email Extractor")
st.write("Paste your target website links below (one per line) to scan them for contact emails.")

urls_input = st.text_area("Target URLs:", height=200, placeholder="example.com\nhttps://another-site.org")

if st.button("Extract Emails", type="primary"):
    urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
    
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        st.subheader("Processing Results")
        all_found_emails = []
        
        for url in urls:
            with st.spinner(f"Scanning: {url}..."):
                emails, status = extract_emails_from_url(url)
                
            if status == "Success":
                if emails:
                    st.success(f"🔗 **{url}** — Found {len(emails)} email(s)")
                    for email in emails:
                        st.code(email, language="text")
                        all_found_emails.append(email)
                else:
                    st.info(f"🔗 **{url}** — No emails found on the homepage.")
            else:
                st.error(f"🔗 **{url}** — {status}")
        
        st.markdown("---")
        if all_found_emails:
            unique_all = sorted(list(set(all_found_emails)))
            st.subheader("📋 All Extracted Emails (Combined)")
            combined_text = "\n".join(unique_all)
            st.text_area("Click inside and press Ctrl+A / Ctrl+C to copy all:", value=combined_text, height=150)
        else:
            st.warning("No emails were extracted.")