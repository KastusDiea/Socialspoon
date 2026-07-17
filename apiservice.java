import dataservice;

public class apiservice{
  private CreatorName creatorname;
  private PlattformName platform;

  public QueryResult shootQuery( CreatorName _c, PlattformName _p){
    //check dataservice for existing info with CreatorData dataservice.getIntel() (throws error if null)
      //if no info, get it from API of _p (possible: YouTube, Instagram, TikTok) with  String _p.getPlattformName()
      //save it to dataservice with dataservice.storeIntel(CreatorData _d)
      //build QueryResult from CreatorData object
    //filter Queryresult with filter()
    //return QueryResult
  }
}
