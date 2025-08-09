<?php
  $s = $_GET['p'];
  $s = base64_decode($s, true); 
  
  $replaced_count_1 = 0;
  $replaced_count_2 = 0;
  $replaced_count_3 = 0;
  str_replace($s, "../", "", $replaced_count_1);
  str_replace($s, "/..", "", $replaced_count_2);
  str_replace($s, "..", "", $replaced_count_3);

  if ($replaced_count_1 + $replaced_count_2 + $replaced_count_3 != 0) {
    die();
  }

  @readfile("./" . $s);
?>
