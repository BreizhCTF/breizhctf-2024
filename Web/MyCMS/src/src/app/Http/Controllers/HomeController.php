<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Flag;

class HomeController extends Controller
{
    public function index()
    {
        $flag = Flag::find(1);
        $flag_value = "";
        if($flag->display)
        {
            $flag_value = $flag->value;
        }
        return view('home', ['flag' => $flag_value]);
    }
}
