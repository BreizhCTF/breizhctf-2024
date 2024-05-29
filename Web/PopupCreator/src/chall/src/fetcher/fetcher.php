<?php
session_start();

error_reporting(0);

include 'helpers/html_parser.php';

header("Content-Type: Application/json");

if($_SERVER["REQUEST_METHOD"] === "POST")
{
    if(isset($_POST["url"]) && !empty($_POST["url"]))
    {
        if(filter_var($_POST["url"], FILTER_VALIDATE_URL))
        {
            if(str_starts_with($_POST['url'],"http://") || str_starts_with($_POST['url'],"https://"))
            {
                $opts = [
                    "http" => [
                        "method" => "GET",
                        "header" => "User-Agent: Popup Website Creator v0.2 Alpha (report any abuse to wedontcare@bullshit.corp)\r\n",
                        "follow_location" => false
                    ],
                    "https" => [
                        "method" => "GET",
                        "header" => "User-Agent: Popup Website Creator v0.2 Alpha (report any abuse to wedontcare@bullshit.corp)\r\n",
                        "follow_location" => false
                    ]
                ];
                $context = stream_context_create($opts);

                //to handle network connection problem
                try{
                    $html = file_get_contents($_POST["url"], false, $context);
                }
                catch(Throwable $e){}
                if(isset($html) && $html != NULL)
                {
                    $parser = new HtmlParser($html);
                    $parser->parse_html();

                    $data = array(
                        "title" => $parser->title,
                        "image" => $parser->image_parser->img_data[0]
                    );
                    
                    if(sizeof($parser->image_parser->img_data) > 1)
                    {
                        $data["image2"] = $parser->image_parser->img_data[1];
                    }
                }
                else
                {
                    $error = "Error while parsing your website.";
                }
            }
            else
            {
                $error = "URL is not valid.";
            }
        }
        else
        {
            $error = "URL is not valid.";
        }
    }
    else
    {
        $error = "Missing 'url' post parameter.";
    }
    
    if(isset($error))
    {
        echo json_encode(array("error" => $error));
    }
    elseif(isset($data))
    {
        echo json_encode(array("data" => $data));
    }
    else
    {
        echo json_encode(array("error" => "Unknown error."));
    }
}
else
{
    echo json_encode(array("error" => "Method not allowed."));
}