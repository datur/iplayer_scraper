# Todo

    [ ] scrape episode/all to gather gather better series information
    [ ] use imdbpy to get progam id and other information
    [ ] rotten tomatoes coming out this week
    [ ] argparse

## todo from 20/02

    [ ] convert json to rdf
    [ ] scrape rotten tomatoes
    [ ] get imdb id
        [ ] criteria if it was on bbc and credits match maybe
        [ ] if cannot locate
        [ ] go through the credits entities and search for a credit [ ] matching show name
    [ ] get credits people imdb id
    [ ] complete
    [/] tvdb search function
    [ ] scrape bbc by series
    [ ] fix ccbc entries
    [ ] brand -> series -> episode
    [ ] programme website get genre format
    [ ] go through each episode page
    [ ] film profile - check out the tags for episodes as not currently working - film nght too
    [ ] for past episodes get broadcast info last on ttag
    [ ] change time left to available untill date
    [ ] air date air time
    [ ] iplayer alphabet suffix -> programmes for that suffix -> programme website extraction(synopsis, genre etc) -> episodes -> all -> season by season episode extraction -> episode page -> credits, episode synopsis, recommendations

    major restructure is required as current structure does not make sense

    full extract structure as follows:
        = loop a through z
            = loop through each program on current alphabet entry
            = get latest episode url / get program general info ie name, and short synopsis
            = visit latest episode site to access program website
                = if program website unavailable then get info from curr page
            = from program website get - long synopsis, airing information, recommendations, genre, format
            = visit episode section if available
            = go through and get all available episodes and follow link for longer synopsis and credits and genre format
            - go through upcoming episodes if available
            - go through all tab for more indepth series information
            - get music played on episode
