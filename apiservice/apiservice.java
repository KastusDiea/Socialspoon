import java.util.ArrayList;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;

public class ApiService {
    private String youtubeAPIKey;

    public ArrayList<Video> getRecentVideos(Platform platform, CreatorName _c) {

        ArrayList<Video> videos = new ArrayList<>();

            // TODO:
            // Parse last 10 uploads with view,like-count, creator name (plus subscriber count), their titles and the upload date from youtube assume youtubeAPIKey is given
            //throw error if yt api key is null or platform is null or _c is null or the api throws an error
            // save them with Video class (title,views,likes,upload-date) CreatorData class (creator name, platform, subscribers, videos (this is a list)) from dataservice.py as object CreatorData cd
            //return cd
            

        return videos;
    }

    public void set_yt_api_key(String _k){
        this.youtubeAPIKey = _k;
    }
}
