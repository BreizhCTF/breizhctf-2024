<?php

namespace App;

class CustomSessionHandler{
    public static function is_session_param_defined($param, $request)
    {
        if($request->session()->get($param) || isset($_SESSION[$param]))
        {
            return true;
        }
        return false;
    }
}
