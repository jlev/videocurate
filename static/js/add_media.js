DEBUG = false;

$(document).ready(function onload(){
  //enable the preview button
  $("input#id_url").keypress(function(e){
    //if the user hits return, process the preview button, not the form submit
    if(e.which == 13) {
      $("input#id_preview_button").click();
      e.preventDefault();
    }
  });
  $("input#id_preview_button").click(function() {
    theURL=$("#id_url").val();
    if (theURL == "") { $("label[for=id_url]").addClass("error"); return false; }
    else { $("label[for=id_url]").removeClass("error"); }
    $("#preview").show();
    $.post("/embed/cache/",{url:theURL,maxwidth:"600"},
      function embedly_callback(data) {
        if (DEBUG) console.log('embedly callback');
        if (DEBUG) console.log(data);
        $('#preview #preview_html').html(data.html);
        $('#addform #id_title').val(data.title);
        $('#addform #id_author_name').val(data.author_name);
        $('#addform #id_author_url').val(data.author_url);
        $('#addform #id_resolution').val(data.width+'x'+data.height);
        $('#preview #preview_description').html(data.description);
        thirdparty_extras(data);
        $("#preview .spinner").hide();
      }
    );
    return false;
  });
  
  $("input#addform_submit").click(function() {
    //do some validation client side, so we don't have to reload the page for missing fields
    required_fields = ["url","title","location","name","review","tags","date_uploaded"]
    has_error = false;
    for (i in required_fields) {
      selector = "id_"+required_fields[i];
      if($('#addform #'+selector).val() == "") {
        has_error = true;
        $("label[for="+selector+"]").addClass("error");
      }
    }
    return !(has_error);
    //false to stop event propagation
    //true to allow
  });

});

/* functionality to get info that embedly doesn't return*/
function thirdparty_extras(data) {
  switch (data.provider_name) {
    case 'YouTube':
      return youtube_extras(data);
    case 'Vimeo':
      return vimeo_extras(data);
    case 'Flickr':
      return flickr_extras(data);
    default:
      return false;
  }
}
function youtube_extras(data) {
  youtube_query = data.url.split('=')[1] //probably good enough, gets the whole query string
  youtube_extra = $.get("https://gdata.youtube.com/feeds/api/videos?",
    {q:youtube_query,max_results:1,v:2,alt:'json'},
    function youtube_callback(response) {
      if (DEBUG) console.log('youtube callback');
      if (DEBUG) console.log(response);
      extra = {}
      entry = response.feed.entry[0];
      extra.views = entry.yt$statistics.viewCount;
      extra.license = entry.media$group.media$license.$t;
      extra.date_uploaded = entry.updated.$t;
      //need to find max width/height
      append_extras(extra);
      return extra;
    });
}
function vimeo_extras(data) {
  //check for trailing slash
  last_char = data.original_url.slice(data.original_url.length-1);
  if (last_char == "/") {
    split_list = data.original_url.split('/');
    vimeo_id = split_list[split_list.length-2];
  } else {
    vimeo_id = data.original_url.split('/').pop();
  }
  vimeo_url = "http://vimeo.com/api/v2/video/" + vimeo_id + ".json";
  vimeo_extra = $.ajax({url:vimeo_url,
                      dataType:'jsonp',
                      success: function vimeo_callback(response,status,jqXHR) {
                        console.log('vimeo callback');
                        console.log(response);
                        item = response[0];
                        append_extras({
                          views:item.stats_number_of_plays,
                          date_uploaded:item.upload_date,
                          //api doesn't return license or max_res
                        })
                      }
                  });
}
function flickr_extras(data) {
  //use regex to determine photo_id
  flickr_regex = RegExp('photos/[^/]+/([0-9]+)')
  photo_id = flickr_regex.exec(data.original_url)[1]
  api_key = 'fd34c2ff0085800fd5c78c24c2b26f66'
  flickr_url = "http://www.flickr.com/services/rest/?method=flickr.photos.getInfo&format=json" +
              "&photo_id=" + photo_id +
              "&api_key=" + api_key;
  flickr_extra = $.ajax({url:flickr_url,
                    dataType:'jsonp',
                    jsonp:'jsoncallback',
                    success: function flickr_callback(response,status,jqXHR) {
                      if (DEBUG) console.log('flickr callback');
                      if (DEBUG) console.log(response);
                      flickr_license = response.photo.license;
                      //see http://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
                      switch(flickr_license) {
                        case 0: license = "unk";
                        case 1: license = "cc-by-nc-sa";
                        case 2: license = "cc-by-nc";
                        case 3: license = "cc-by-nc-nd";
                        case 4: license = "cc-by";
                        case 5: license = "cc-by-sa";
                        case 6: license = "cc-by-nd";
                        case 7: license = "none";
                        default: license = "unk";
                      }
                      append_extras({
                        views:response.photo.views,
                        license:license,
                        date_uploaded:response.photo.dates.taken //uses exif data, parse in python
                      })
                    }
                  });
}
function append_extras(extra) {
  // save the extra data to the input fields
  if (extra.max_width && extra.max_height){
    $('#addform #id_resolution').val(extra.max_width+'x'+extra.max_height); 
  };
  if (extra.views) { $('#addform #id_views').val(extra.views); }
  if (extra.license) { $('#addform #id_license').val(extra.license); }
  if (extra.date_uploaded) { $('#addform #id_date_uploaded').val(extra.date_uploaded); }
}