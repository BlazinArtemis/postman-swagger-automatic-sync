import requests
import random

BASE_URL = "http://127.0.0.1:8000"

# Sample data
urls = [
    "https://example.com",
    "https://fastapi.tiangolo.com",
    "https://github.com",
    "https://stackoverflow.com",
    "https://www.python.org",
    "https://realpython.com",
    "https://www.djangoproject.com",
    "https://flask.palletsprojects.com",
    "https://www.sqlalchemy.org",
    "https://www.sqlite.org",
    "https://pandas.pydata.org",
    "https://numpy.org",
    "https://scipy.org",
    "https://matplotlib.org",
    "https://seaborn.pydata.org",
    "https://jupyter.org",
    "https://ipython.org",
    "https://www.tensorflow.org",
    "https://pytorch.org",
    "https://keras.io"
]

titles = [
    "Example Site",
    "FastAPI Documentation",
    "GitHub",
    "Stack Overflow",
    "Python Official Site",
    "Real Python",
    "Django",
    "Flask",
    "SQLAlchemy",
    "SQLite",
    "Pandas",
    "NumPy",
    "SciPy",
    "Matplotlib",
    "Seaborn",
    "Jupyter",
    "IPython",
    "TensorFlow",
    "PyTorch",
    "Keras"
]

descriptions = [
    "A sample site for examples.",
    "Documentation for FastAPI.",
    "A platform for open source code.",
    "Q&A site for programming.",
    "Official Python website.",
    "Python tutorials and articles.",
    "A high-level Python web framework.",
    "A micro web framework for Python.",
    "The Python SQL toolkit.",
    "Self-contained, serverless, SQL database engine.",
    "Data analysis and manipulation tool.",
    "Library for large array and matrix processing.",
    "Library for scientific computing.",
    "Comprehensive library for creating static, animated, and interactive visualizations.",
    "Statistical data visualization library.",
    "A web application to create and share documents that contain live code, equations, visualizations, and narrative text.",
    "A rich architecture for interactive computing.",
    "An end-to-end open-source platform for machine learning.",
    "An open-source machine learning library based on the Torch library.",
    "A deep learning API written in Python, running on top of the machine learning platform TensorFlow."
]

tags = ["tech", "education", "programming", "python", "machine learning", "web development"]

def create_tag(tag_name):
    response = requests.post(f"{BASE_URL}/tags", json={"name": tag_name})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to create tag: {tag_name}")
        return None

def create_bookmark(url, title, description=None, tag_ids=None):
    data = {
        "url": url,
        "title": title,
        "description": description
    }
    response = requests.post(f"{BASE_URL}/bookmarks", json=data)
    if response.status_code == 200:
        bookmark = response.json()
        if tag_ids:
            for tag_id in tag_ids:
                requests.post(f"{BASE_URL}/bookmarks/{bookmark['id']}/tags/{tag_id}")
        return bookmark
    else:
        print(f"Failed to create bookmark: {url}")
        return None

def main():
    # Create tags
    tag_id_map = {}
    for tag in tags:
        created_tag = create_tag(tag)
        if created_tag:
            tag_id_map[tag] = created_tag["id"]

    # Create bookmarks
    for i in range(20):
        url = urls[i]
        title = titles[i]
        description = random.choice(descriptions) if random.choice([True, False]) else None
        tag_ids = random.sample(list(tag_id_map.values()), k=random.randint(0, 3)) if random.choice([True, False]) else None
        create_bookmark(url, title, description, tag_ids)

if __name__ == "__main__":
    main()

