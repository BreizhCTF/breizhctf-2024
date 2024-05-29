<?php

include 'image_parser.php';

class HtmlParser
{

    function __construct($html)
    {
        $this->raw_html = $html;
        $this->title = "";
        $this->image_parser = new ImageParser();
        $this->dom_doc = NULL;
        $this->images = array();
        $this->nb_max_images = 2;
    }

    function parse_html()
    {
        $this->dom_doc = new DOMDocument();
        $this->dom_doc->loadHTML($this->raw_html);
        $this->get_title();

        if($this->title == "")
        {
            $this->title = "No title found on your website.";
        }

        $this->get_images();
        $this->image_parser->parse_image($this->images);
        if(sizeof($this->image_parser->img_data) == 0)
        {
            array_push($this->image_parser->img_data, base64_encode("No image found"));
        }
    }

    function get_title()
    {
        $elements = $this->dom_doc->getElementsByTagName('title');
        if(sizeof($elements) > 0)
        {
            foreach($elements as $element)
            {
                if(!empty($element->nodeValue))
                {
                    $this->title = htmlspecialchars($element->nodeValue);
                    break;
                }
            }
        }
    }

    function get_images()
    {
        $elements = $this->dom_doc->getElementsByTagName('img');
        if(sizeof($elements) > 0)
        {
            $nb_image = 0;
            foreach($elements as $element)
            { 
                if($nb_image >= $this->nb_max_images) break;

                if(!empty($element->getAttribute('src')))
                {
                    array_push($this->images, $element->getAttribute('src'));
                    $nb_image++;
                }
            }
        }
    }
}