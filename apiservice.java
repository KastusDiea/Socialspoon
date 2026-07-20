import dataservice;
import dataTransformService;

public class apiservice{
  private CreatorName creatorname;
  private PlattformName platform;

  public QueryResult shootQuery(CreatorName creator, PlattformName platform) {
    CreatorData data = dataservice.getIntel(creator, platform);
    if (data == null) {
        data = ApiFactory
                .getApi(platform)
                .loadCreatorData(creator);
        dataservice.storeIntel(data);
    }
    return filter(data);
  }

  public QueryResult filter(CreatorData){
    return dataTransformService.filter(CreatorData);
  }
}
