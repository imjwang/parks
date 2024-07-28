from tqdm import tqdm
from langchain_community.utilities import GoogleSerperAPIWrapper
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


PARKS = [
    "Acadia National Park",
    "Arches National Park",
    "Badlands National Park",
    "Big Bend National Park",
    "Biscayne National Park",
    "Black Canyon of the Gunnison National Park",
    "Bryce Canyon National Park",
    "Canyonlands National Park",
    "Capitol Reef National Park",
    "Carlsbad Caverns National Park",
    "Channel Islands National Park",
    "Congaree National Park",
    "Crater Lake National Park",
    "Cuyahoga Valley National Park",
    "Death Valley National Park",
    "Denali National Park",
    "Dry Tortugas National Park",
    "Everglades National Park",
    "Gates of the Arctic National Park",
    "Gateway Arch National Park",
    "Glacier Bay National Park",
    "Glacier National Park",
    "Grand Canyon National Park",
    "Grand Teton National Park",
    "Great Basin National Park",
    "Great Sand Dunes National Park",
    "Great Smoky Mountains National Park",
    "Guadalupe Mountains National Park",
    "Haleakala National Park",
    "Hawai'i Volcanoes National Park",
    "Hot Springs National Park",
    "Indiana Dunes National Park",
    "Isle Royale National Park",
    "Joshua Tree National Park",
    "Katmai National Park",
    "Kenai Fjords National Park",
    "Kings Canyon National Park",
    "Kobuk Valley National Park",
    "Lake Clark National Park",
    "Lassen Volcanic National Park",
    "Mammoth Cave National Park",
    "Mesa Verde National Park",
    "Mount Rainier National Park",
    "National Park of American Samoa",
    "New River Gorge National Park and Preserve",
    "North Cascades National Park",
    "Olympic National Park",
    "Petrified Forest National Park",
    "Pinnacles National Park",
    "Redwood National Park",
    "Rocky Mountain National Park",
    "Saguaro National Park",
    "Sequoia National Park",
    "Shenandoah National Park",
    "Theodore Roosevelt National Park",
    "Virgin Islands National Park",
    "Voyageurs National Park",
    "White Sands National Park",
    "Wind Cave National Park",
    "Wrangell—St. Elias National Park",
    "Yellowstone National Park",
    "Yosemite National Park",
    "Zion National Park"
]

SEASHORES = [
    "Assateague Island",
    "Canaveral",
    "Cape Cod",
    "Cape Hatteras",
    "Cape Lookout",
    "Cumberland Island",
    "Fire Island",
    "Gulf Islands",
    "Padre Island",
    "Point Reyes"
]

LAKESHORES = [
    "Apostle Islands",
    "Pictured Rocks",
    "Sleeping Bear Dunes"
]

# Function to download an image with error handling


def download_image(url, filename):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return None


def get_image_urls(park):
    # Replace 'search.results' with your actual search function
    results = search.results(park)["images"]
    return [r['imageUrl'] for r in results]


search = GoogleSerperAPIWrapper(type="images")


def main():

    tasks = []

    for park in PARKS:
        urls = get_image_urls(park)
        for idx, url in enumerate(urls):
            filename = f"imgs/data/{park}_{idx}.jpeg"
            tasks.append((url, filename))

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_task = {executor.submit(download_image, url, filename): (
            url, filename) for url, filename in tasks}
        for future in tqdm(as_completed(future_to_task), total=len(future_to_task)):
            url, filename = future_to_task[future]
            try:
                result = future.result()
                if result:
                    print(f"Successfully downloaded {result}")
            except Exception as e:
                print(f"Error downloading {url}: {e}")


if __name__ == "__main__":
    main()
