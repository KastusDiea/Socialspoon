publich class Platform() {
    private String platformName;
    private String apikey = 0;

    public Platform(String _n, String _api){
        if(_n.equals("YouTube") || _n.equals("Instagram") || _n.equals("TikTok")){
            this.platformName = _n;
        }
        this.apikey = _api;

    }
    
    
    public String getName(){
        return platformName;
    }


    public String getApiKey(){
        return this.apikey;
    }

    
}