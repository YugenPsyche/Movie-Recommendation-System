import requests
import streamlit as st
import pickle
import pandas as pd


# Function to fetch poster from TMDB API
def fetch_poster(movie_id):
    try:
        api_key = ""# Enter your API key
      
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image+Available"
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Error+Fetching+Image"


# Function to recommend movies based on similarity
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(
            list(enumerate(similarity[index])),
            reverse=True,
            key=lambda x: x[1]
        )

        recommended_movies = []
        recommended_movies_posters = []
        recommended_movie_ids = []

        for i in distances[1:9]:  # Top 8 recommendations
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))
            recommended_movie_ids.append(movie_id)

        return recommended_movies, recommended_movies_posters, recommended_movie_ids
    except IndexError:
        st.error("Movie not found in the dataset!")
        return [], [], []
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return [], [], []


# Function to fetch detailed movie information
def fetch_movie_details(movie_id):
    try:
        api_key = "8265bd1679663a7ea12ac168da84d2e8"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        title = data.get('title')
        overview = data.get('overview')
        rating = data.get('vote_average')
        release_date = data.get('release_date')
        genres = [genre['name'] for genre in data.get('genres', [])]
        streaming_info = get_streaming_links(movie_id)

        return {
            'title': title,
            'overview': overview,
            'rating': rating,
            'release_date': release_date,
            'genres': genres,
            'streaming_info': streaming_info
        }
    except Exception as e:
        st.error(f"Error fetching movie details: {e}")
        return None


# Function to fetch streaming platform links for the movie
def get_streaming_links(movie_id):
    try:
        api_key = "8265bd1679663a7ea12ac168da84d2e8"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        streaming_providers = data.get('results', {}).get('US', {}).get('flatrate', [])
        providers = {provider['provider_name']: provider['logo_path'] for provider in streaming_providers}

        return providers
    except Exception as e:
        st.error(f"Error fetching streaming links: {e}")
        return {}


# Load movie data and similarity matrix
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError as e:
    st.error("Required files are missing. Please ensure 'movie_dict.pkl' and 'similarity.pkl' exist.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred while loading data: {e}")
    st.stop()

# Streamlit UI
st.title('Movie Recommendations System')

# Create a sidebar for user account creation
with st.sidebar:
    st.header("Account Creation")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if password == confirm_password and username:
            st.success("Account created successfully!")
        elif password != confirm_password:
            st.error("Passwords do not match!")
        elif not username:
            st.error("Please enter a username.")
        else:
            st.error("Error creating account.")

    # Add a note about account creation
    st.subheader("How Account Creation Helps:")
    st.write("""
        By creating an account, you will be able to:
        - Directly **book movie tickets** or **subscribe to services**.
        - Receive **personalized movie recommendations** tailored to your preferences.
        - Your data will be analyzed to **improve your user experience** and provide **better content suggestions**.
    """)

# Dropdown for movie selection
selected_movie_name = st.selectbox(
    "Type or select a movie from the dropdown",
    movies['title'].values
)

# Recommendation button
if st.button('Recommend'):
    names, posters, movie_ids = recommend(selected_movie_name)

    if names and posters:
        cols = st.columns(4)  # Create 4 columns for recommendations
        for i, col in enumerate(cols):
            with col:
                # Display each recommended movie with an image and a button to show details below it
                st.image(posters[i], width=250)  # Movie poster displayed here
                movie_details = fetch_movie_details(movie_ids[i])

                if movie_details:
                    # Display detailed information of the movie below the poster
                    st.subheader(f"Details for {names[i]}")
                    st.image(posters[i], width=300)  # Larger poster
                    st.write(f"**Overview:** {movie_details['overview']}")
                    st.write(f"**Rating:** {movie_details['rating']}/10")
                    st.write(f"**Release Date:** {movie_details['release_date']}")
                    st.write(f"**Genres:** {', '.join(movie_details['genres'])}")

                    st.write("**Available on the following platforms:**")
                    if movie_details['streaming_info']:
                        for provider, logo in movie_details['streaming_info'].items():
                            logo_url = f"https://image.tmdb.org/t/p/w200{logo}"
                            st.image(logo_url, width=50, caption=provider)
                    else:
                        st.write("No streaming information available.")
