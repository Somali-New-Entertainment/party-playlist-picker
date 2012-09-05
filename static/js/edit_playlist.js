/*
Copyright 2012 Google Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// This is an anonymous module.
(function() {
  var ID_PATTERN = 'data-video-li-id="(.+?)"';
  var GLOBAL_ID_REGEX = new RegExp(ID_PATTERN, 'g');
  var CAPTURE_ID_REGEX = new RegExp(ID_PATTERN);
  var ANIMATION_TIMEOUT = 1000;

  var player;
  var cuedVideo;

  // Given a string, HTML escape it.
  function escapeHTML(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // Apply all the handlers for a playlist.
  function bindPlaylistHandlers() {
    bindRemoveHandlers();
    $("#playlist ul").sortable().disableSelection();
    $("#playlist ul").bind("sortupdate", function(event, ui) {
      var li = ui.item[0];
      var $li = $(li);
      var position = $li.index() + 1;
      var liId = li.id.replace(/^li-/, '');
      var url;
      if ($li.hasClass('playlist-item')) {
        url = ('/playlists/edit/' + encodeURIComponent(playlistId) +
               '/move_playlist_entry?uri=' + encodeURIComponent(liId) +
               '&position=' + position);
      } else if ($li.hasClass('search-item')) {
        url = ('/playlists/edit/' + encodeURIComponent(playlistId) +
               '/add_playlist_entry?position=' + position + '&video_id=' +
               encodeURIComponent(liId));
      } else {
        return;
      }
      url += '&uuid=' + encodeURIComponent(uuid);
      $.ajax({ type: 'POST', url: url });
    });
  }
  
  // Find all remove buttons and add an onClick handler to call our removal server-side code.
  function bindRemoveHandlers() {
    $(".remove-button").bind("click", function(event) {
      $(this).attr("disabled", "disabled");
      var url = ('/playlists/edit/' + encodeURIComponent(playlistId) +
                 '/remove_playlist_entry?uri=' + encodeURIComponent(event.target.id) +
                 '&uuid=' + encodeURIComponent(uuid));
      $.ajax({ type: 'POST', url: url });
    });
  }
  
  // Add handlers to search results after they're inserted into the page.
  function bindSearchResultHandlers() {
    bindAddHandlers();
    enableSorting();
  }
  
  // Find all add buttons and add an onClick handler to call our server-side code to add the video to the playlist.
  function bindAddHandlers() {
    $(".add-button").bind("click", function(event) {
      $(this).attr("disabled", "disabled");
      $(this).closest('li').hide('blind', { direction: 'vertical' }, ANIMATION_TIMEOUT);
      var url = ('/playlists/edit/' + encodeURIComponent(playlistId) +
                 '/add_playlist_entry?video_id=' + encodeURIComponent(event.target.id) +
                 '&uuid=' + encodeURIComponent(uuid));
      $.ajax({ type: 'POST', url: url });
    });
  }

  // Enable sorting on the newly added search results list.
  // TODO: Don't let the user reorder search results.
  function enableSorting() {
    $("#search-results ul").sortable({connectWith: '#playlist ul'}).disableSelection();
  }

  // When the user searches for something, do a YouTube search.  
  function bindSearchHandler() {
    $("#search-form").submit(function() {
      var q = $("#q").val();
      if (q !== "") {
        $.ajax({
          dataType: 'html',
          url: '/search?q=' + encodeURIComponent(q),
          
          // Show the user his search results.
          success: function(response) {
            $("#search-results").html(response);            
            bindSearchResultHandlers();
          }
        });
      }
    
      return false;
    });
  }

  // Make all playable video thumbnails play back the YouTube video when clicked.
  // On mouseenter, show the play overlay, and hide on mouseleave.
  function bindVideoThumbnailHandlers() {
    $(".playable-thumbnail-image").live("click", function(event) {
      playVideoFromThumbnailUrl($(this).attr('src'));
    });

    $(".play-overlay").live("click", function(event) {
      playVideoFromThumbnailUrl(
        $(this).prev('.playable-thumbnail-image').attr('src'));
    });

    $(".video-thumbnail").live("mouseenter", function(event) {
      // There won't be any matches if the video isn't embeddable.
      $(this).find('.play-overlay').fadeIn();
    });

    $(".video-thumbnail").live("mouseleave", function(event) {
      // There won't be any matches if the video isn't embeddable.
      $(this).find('.play-overlay').fadeOut();
    });
  }

  // Given a thumbnail URL, get the video id and initiate playback.
  // TODO: Use something other than string splitting.
  function playVideoFromThumbnailUrl(thumbnailUrl) {
    var videoId = thumbnailUrl.split('/')[4];
    if (videoId != null) {
      playVideo(videoId);
    }
  }

  // When the user clicks on the background during video playback or presses
  // Esc, stop playback and hide the video.
  function bindVideoHidingHandlers() {
    $('#yt-player-container').click(hideVideo);
    $(document).keyup(function(event) {
      // Check for the Esc key.
      if (event.keyCode == 27) {
        hideVideo();
      }
    });
  }
  
  // Use a diff algorithm to gracefully show and remove videos as they
  // are added or removed from the playlist.
  function updatePlaylist(newHtml) {
    var oldHtml = $('#playlist').html();
    
    // See http://code.google.com/p/google-diff-match-patch/wiki/API
    // for documentation on the Diff, Match, and Patch Library.
    var differ = new diff_match_patch();
    var diffs = differ.diff_main(oldHtml, newHtml);
    differ.diff_cleanupSemantic(diffs);
    
    // Keep track of all additions and removals. Many people might be editing
    // at once, so we can't assume there will only be one changed element.
    var additionIds = [];
    var removalIds = [];
    $.each(diffs, function(i, diff) {
      // diff[0] values:
      //   1 => addition
      //   0 => equivalent
      //  -1 => removal
      // diff[1] is the corresponding snippet of text.
      
      // Find all the Id: comment strings, if any.
      var matches = diff[1].match(GLOBAL_ID_REGEX);
      if (matches) {
        $.each(matches, function(j, match) {
          // Grab the id value from the comment string.
          // It would be nice to do this from the original regex using
          // capturing () there, but string.match(//g) doesn't respect them.
          var id = match.match(CAPTURE_ID_REGEX)[1];
          if (diff[0] == 1) {
            additionIds.push(id);
          } else if (diff[0] == -1) {
            removalIds.push(id);
          }
        });
      }
    });
    
    // If we don't have any removal animation, then fire the addition
    // animation right away. Otherwise, wait until the removal animation
    // completes (more or less) before handling additions.
    var additionsTimeoutInterval = 0;
    if (removalIds.length) {
      additionsTimeoutInterval = ANIMATION_TIMEOUT;
    }
    
    $.each(removalIds, function(i, removalId) {
      // Start these removal animations before we have replaced the old HTML.
      var element = $(document.getElementById(removalId));
      element.hide('blind', { direction: 'vertical' }, ANIMATION_TIMEOUT);
    });
    
    setTimeout(function() {
      // This executes unconditionally, since we always want to update the
      // HTML even if we don't have any additions.
      $('#playlist').html(newHtml);
      handleUpdatesTo('playlist');
      
      $.each(additionIds, function(i, additionId) {
        var element = $(document.getElementById(additionId));
        element.hide();
        element.show('blind', { direction: 'vertical' }, ANIMATION_TIMEOUT);
      });
    }, additionsTimeoutInterval);
  }
  
  // Call this explicitly if the element with the given id changes.
  // We're doing this inline for the time being, but it could easily
  // be changed into a registry.
  function handleUpdatesTo(id) {
    if (id == 'playlist') {
      bindPlaylistHandlers();
    }
  }
  
  // Handle a message from the channel API.
  function handleChannelMessage(message) {
    var json = $.parseJSON(message.data);
    if (json.action == "updateElement") {
      if (json.id == "playlist") {
        updatePlaylist(json.html);
      } else {
        $('#' + json.id).html(json.html);
        handleUpdatesTo(json.id);
      }
    }
  }
  
  // Display a notification.
  function displayNotification(notification) {
    $('#notification').html(notification);
    $('#notification').fadeIn('slowest');
  }
  
  // Open a connection using the Channel API when the page loads.
  function openChannelConnection() {
    $.ajax({
      type: 'POST',
      dataType: 'json',
      url: ('/playlists/edit/' + encodeURIComponent(playlistId) +
            '/generate_channel_token' +
            '?uuid=' + encodeURIComponent(uuid)),
      success: function(json) {
        var channel = new goog.appengine.Channel(json.channelToken);
        var socket = channel.open();
        socket.onerror = function() { displayNotification('Unable to communicate with server. Try <a href="javascript:window.location.reload();">reloading</a> the page.'); };
        socket.onmessage = function(message) { handleChannelMessage(message); };
      }
    });
  }

  // Plays a YouTube video in an iframe player.
  // Load the player if this is the first call; otherwise, reuse the existing
  // player instance.
  function playVideo(videoId) {
    $('#yt-player-container').fadeIn();

    if (player == null) {
      cuedVideo = videoId;
      $.getScript('http://www.youtube.com/player_api');
    } else {
      player.loadVideoById(videoId);
    }
  }

  // Called by the iframe player API when it's finished loading.
  // This needs to be in the window's context so that the external JS file
  // can call it.
  window.onYouTubePlayerAPIReady = function() {
    player = new YT.Player('yt-player', {
      videoId: cuedVideo,
      events: {
        onReady: function() { player.playVideo(); }
      }
    });
  };

  // Stops video playback and hides the player and container.
  // Harmless to call even if the player isn't initialized or visible.
  function hideVideo() {
    if (player != null) {
      player.stopVideo();
    }
    $('#yt-player-container').fadeOut();
  }

  // On load.
  $(function() {
    bindPlaylistHandlers();
    bindSearchHandler();
    bindVideoThumbnailHandlers();
    bindVideoHidingHandlers();
    openChannelConnection();

    // Use an empty onBeforeUnload handler to ensure that our page is refreshed
    // if the user navigates back to it after visiting another page.
    $(window).bind('beforeunload', function() {});
  });
})();