import dataservice;
import dataTransformService;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class apiservice{
  private CreatorName creatorname;
  private PlattformName platform;
  private final DataService dataService;
  private final DataTransformService dataTransformService;
  private final HttpClient httpClient;
  private final ObjectMapper mapper;
  private static final String YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY";
  private static final String INSTAGRAM_TOKEN = "YOUR_INSTAGRAM_TOKEN";
  private static final String TIKTOK_TOKEN = "YOUR_TIKTOK_TOKEN";

  public apiservice(DataService dataService, DataTransformService dataTransformService) {
      this.dataService = dataService;
      this.dataTransformService = dataTransformService;
      this.httpClient = HttpClient.newHttpClient();
      this.mapper = new ObjectMapper();
  }

  public QueryResult shootQuery(CreatorName creator, PlattformName platform) throws IOException, InterruptedException {
      CreatorData creatorData;
      try {
            creatorData = dataService.getIntel(creator);
        } catch (Exception e) {
            switch (platform.getPlattformName()) {

                case "YouTube":
                    creatorData = fetchYouTubeData(creator);
                    break;

                case "Instagram":
                    creatorData = fetchInstagramData(creator);
                    break;

                case "TikTok":
                    creatorData = fetchTikTokData(creator);
                    break;

                default:
                    throw new IllegalArgumentException("Unsupported platform: " + platform.getPlattformName());
            }
            dataService.storeIntel(creatorData);
        }
        return filter(creatorData);
    }

    public QueryResult filter(CreatorData creatorData) {
        return dataTransformService.filter(creatorData);
    }



    private CreatorData fetchYouTubeData(CreatorName creator) throws IOException, InterruptedException {
        String url =
                "https://www.googleapis.com/youtube/v3/channels"
                        + "?part=snippet,statistics"
                        + "&forUsername="
                        + URLEncoder.encode(creator.toString(),
                        StandardCharsets.UTF_8)
                        + "&key=" + YOUTUBE_API_KEY;

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();

        HttpResponse<String> response =
                httpClient.send(request,
                        HttpResponse.BodyHandlers.ofString());

        JsonNode root = mapper.readTree(response.body());
        JsonNode item = root.get("items").get(0);

        CreatorData data = new CreatorData();

        data.setCreatorName(creator);
        data.setPlatform("YouTube");
        data.setDisplayName(item.get("snippet").get("title").asText());
        data.setDescription(item.get("snippet")
                .get("description").asText());
        data.setSubscribers(
                item.get("statistics")
                        .get("subscriberCount").asLong());
        data.setViews(
                item.get("statistics")
                        .get("viewCount").asLong());
        data.setContentCount(
                item.get("statistics")
                        .get("videoCount").asInt());

        return data;
    }


    private CreatorData fetchInstagramData(CreatorName creator) throws IOException, InterruptedException {
        String url =
                "https://graph.instagram.com/"
                        + creator
                        + "?fields=username,followers_count,media_count"
                        + "&access_token="
                        + INSTAGRAM_TOKEN;

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .GET()
                .build();

        HttpResponse<String> response =
                httpClient.send(request,
                        HttpResponse.BodyHandlers.ofString());

        JsonNode json = mapper.readTree(response.body());

        CreatorData data = new CreatorData();

        data.setCreatorName(creator);
        data.setPlatform("Instagram");
        data.setDisplayName(json.get("username").asText());
        data.setSubscribers(json.get("followers_count").asLong());
        data.setContentCount(json.get("media_count").asInt());

        return data;
    }


    private CreatorData fetchTikTokData(CreatorName creator) throws IOException, InterruptedException {
        String url =
                "https://open.tiktokapis.com/v2/user/info/?username="
                        + URLEncoder.encode(
                        creator.toString(),
                        StandardCharsets.UTF_8);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Authorization",
                        "Bearer " + TIKTOK_TOKEN)
                .GET()
                .build();

        HttpResponse<String> response =
                httpClient.send(request,
                        HttpResponse.BodyHandlers.ofString());

        JsonNode json = mapper.readTree(response.body());
        JsonNode user = json.get("data").get("user");
        CreatorData data = new CreatorData();
        data.setCreatorName(creator);
        data.setPlatform("TikTok");
        data.setDisplayName(user.get("display_name").asText());
        data.setSubscribers(user.get("follower_count").asLong());
        data.setContentCount(user.get("video_count").asInt());
        return data;
    }
}
