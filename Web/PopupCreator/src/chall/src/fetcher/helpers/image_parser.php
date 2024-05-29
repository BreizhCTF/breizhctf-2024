<?php

class ImageParser
{

    function __construct()
    {
        $this->img_data = [];
    }

    function parse_image($images)
    {
        foreach($images as $image)
        {
            try{
                $imagick = new Imagick($image);
                $imagick->resizeImage(25,25, 1, 1);
                array_push($this->img_data, base64_encode($imagick->getImageBlob()));
            }
            catch(Throwable $e){};
        }
    }
}