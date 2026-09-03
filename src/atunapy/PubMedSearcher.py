import time
import pandas as pd
from Bio import Entrez

def fetch_articles(search_terms: list, 
                            retmax: int = 10000, 
                            batch_size: int = 200, 
                            email: str = None, 
                            api_key: str = None, 
                            min_date: str = "1900/01/01",
                            max_date: str = time.strftime("%Y/%m/%d"),
                            reviews: bool = False) -> pd.DataFrame:


    """ Retrieves articles from PubMed based on search terms and date range, returning a DataFrame of results.
        Email and API key are not required, but are recommended for better Entrez API access. 
        The function handles large result sets by splitting searches into year-by-year batches if necessary.
    Args:
        search_terms (list): A list of search terms (str) to query PubMed
        retmax (int): The maximum number of records to retrieve per search term (default is 10000 which is the Entrez limit)
        batch_size (int): The number of records to fetch in each batch (default is 200)
        email (str): The email address for Entrez API access
        api_key (str): The API key for Entrez API access. You can get your own API key here --> https://account.ncbi.nlm.nih.gov/settings/
        min_date (str): The minimum date for the search range (default is "1900/01/01")
        max_date (str): The maximum date for the search range (default is current date)
        reviews (bool): A flag to include review articles in the results (default is False)

    Returns:
        pd.DataFrame: A DataFrame containing metadata from the retrieved articles.
    """
    start_time = time.perf_counter() # Record the start time for performance measurement
    articles = []
    Entrez.email = email
    Entrez.api_key = api_key

    def retrieve_ids(term, retmax=10000, min_date=min_date, max_date=max_date):
        """Retrieve PubMed IDs for a given search term and date range."""
        handle = Entrez.esearch(
            db="pubmed", 
            term=term, 
            retmax=retmax,
            sort="pub_date", 
            datetype="pdat",
            mindate=min_date, 
            maxdate=max_date, 
            usehistory="y"
        )
        record = Entrez.read(handle)
        handle.close()
        return record

    def batch_fetch(webenv, query_key, total_count, batch_size=200):
        """Fetch all records in paginated batches."""
        full_records = []
        start = 0

        while start < total_count:
            batch_fetched = False
            for attempt in range(1, 4):
                try:
                    handle = Entrez.efetch(
                        db="pubmed", webenv=webenv, query_key=query_key,
                        retstart=start, retmax=batch_size, retmode="xml"
                    )
                    records = Entrez.read(handle)
                    handle.close()
                    full_records.extend(records["PubmedArticle"])
                    batch_fetched = True
                    break
                except Exception as e:
                    print(f"\nBatch error at start={start} (Attempt {attempt}/3): {e}")
                    time.sleep(5)

            if not batch_fetched:
                print(f"Skipping batch at start={start} after 3 failed attempts.")
            start += batch_size

        return full_records

    def fetch_by_date_ranges(term, date_ranges):
        """Fetch records across a list of (min_date, max_date) tuples. Only applies if the total number of results exceeds retmax."""
        all_records = []
        for min_d, max_d in date_ranges:
            try:
                rec = retrieve_ids(term, retmax=retmax, min_date=min_d, max_date=max_d)
                count = int(rec["Count"])
                if count == 0:
                    continue
                if count >= retmax:
                    print(f"  Warning: {count} records in {min_d}–{max_d}, may be truncated at {retmax}.")
                records = batch_fetch(rec["WebEnv"], rec["QueryKey"], count, batch_size)
                all_records.extend(records)
                print(f"  Fetched {len(records)} records for {min_d}–{max_d}")
            except Exception as e:
                print(f"  Error fetching {min_d}–{max_d}: {e}")
        return all_records

    for term in search_terms:
        print(f"\nSearching: '{term}'")
        try:
            record = retrieve_ids(term, retmax=retmax)
            count = int(record["Count"])
            print(f"  Total matching records: {count}")
        except Exception as e:
            print(f"  Error retrieving IDs: {e}")
            continue

        if count == 0:
            continue

        elif count < retmax:
            all_records = batch_fetch(record["WebEnv"], record["QueryKey"], count, batch_size)

        else:
            print(f"  Count ({count}) exceeds retmax ({retmax}). Splitting by year...")

            # Build year-by-year ranges from min_date year to current year (inclusive)
            start_year = int(min_date[:4])
            end_year = int(max_date[:4])  # inclusive

            date_ranges = [
                (f"{y}/01/01", f"{y}/12/31")
                for y in range(start_year, end_year + 1)  # +1 to include current year
            ]
            all_records = fetch_by_date_ranges(term, date_ranges)

        # --- Parse records ---
        for article in all_records:
            try:
                citation = article["MedlineCitation"]
                article_data = citation["Article"]
                pmid    = str(citation.get("PMID", "NA"))
                title   = article_data.get("ArticleTitle", "NA")
                abstract = " ".join(
                    article_data.get("Abstract", {}).get("AbstractText", [])
                ) if "Abstract" in article_data else "NA"
                history_dates = article["PubmedData"]["History"]
                year = history_dates[0].get("Year", "NA") if history_dates else "NA"
                doi = "NA"
                for el in article_data.get("ELocationID", []):
                    if el.attributes.get("EIdType") == "doi":
                        doi = str(el)
                        break
                languages = article_data.get("Language", [])
                if "eng" not in languages:
                    continue
                pub_types = article_data.get("PublicationTypeList", [])
                pub = str(pub_types[0]) if pub_types else "NA"
                articles.append({
                    "PMID": pmid, "DOI": doi, "Title": title,
                    "Abstract": abstract, "Year": year, "PublicationTypes": pub
                })
            except Exception as e:
                print(f"  Error parsing article: {e}")
                continue

    # --- Post-processing ---
    df = pd.DataFrame(articles)
    print(f"\nTotal before dedup: {len(df)}")
    df = df.drop_duplicates(subset=["PMID"])
    print(f"Total after dedup:  {len(df)}")
    df = df[(df["Abstract"] != "NA") & (df["Title"] != "NA")]
    df = df.sort_values(by="Year", ascending=False)

    if not reviews:
        valid_types = [
            "Journal Article", "Comparative Study", "Clinical Trial",
            "Randomized Controlled Trial", "Clinical Trial, Phase I",
            "Clinical Trial, Phase II", "Clinical Trial, Phase III", "Case Reports"
        ]
        df = df[df["PublicationTypes"].isin(valid_types)]

    print(f"Total after filtering: {len(df)}")
    print(f"Records retrieved from {min_date} to {max_date}")
    print(df["PublicationTypes"].value_counts())
    print(f"Search completed in {round(time.perf_counter() - start_time, 2)} seconds")
    return df   