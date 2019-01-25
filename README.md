# iplayer scraper

# TODO:

    [ ] Dictionary building for each object in Json Structure
    [ ] Refactoring current code into methods
    [ ] Finish episode page navigation if more than one page of episodes
    [ ] Loop through alphabet 
    [ ] Save to Json
    
    
    
# features
    
    Json Structure
    
    {
        "program_id": {
            "program_name": Silent Witness,
            "program_website": http://bbc.co.uk/programmes/<program_id>,
            "genre": {"main": Drama, "sub": Crime},
            "format": {<(optional field)>},
            "no_episodes_available": 56,
            "no_episodes_upcoming": 4,

            "latest_episode": {
                "title": <text: title>,
                "broadcast_date": <text: date>,
                "broadcast_channel": <text: channel>,
                "days_left_to_watch": <text: days>,
                "duration": <text: minutes>
                "synopsis": <text: short_synopsis>,
                "long_synopsis": <text: longform_synopsis>,
                "url": <url: latest_episode_url>,
                "credits": {
                    "role": <text: person>,
                    ...
                    ...
                    ...}
                },

            "ipayer_recommends": {
                "recommendation_id": {
                    "program_name": <text: show_name>,
                    "program_website": <url: program_website>,
                    "synopsis": <text: short_synopsis>},
                "recommendation_id":{
                    ...
                    ...
                    ...},
                ...
                ...
                },

            "episodes_available": {
                "episode_id": {
                    "episode_name": <text: episode_name>,
                    "episode_link": <url: episode_link>,
                    "program_webpage": <url: program_webpage>,
                    "episode_synopsis": <text: episode_synopsis>
                    },
                 "episode_id": {
                     ...
                     ...
                     ...
                     },
                 ...
                 ...
                 ...
                 },


                
            "upcoming_episodes": {
                "episode_id": {
                    "episode_name": <text: episode_name>,
                    "episode_link": <url: episode_link>,
                    "synopsis": <text: short_synopsis>
                    "air_date": <text: date>,
                    "air_time": <text: time hours>,
                    "air_channel": <text: channel>,
                    "air_day": <text: day>},
                ...
                ...
                ...
                },

    }
