from __future__ import annotations

import json
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from modernrpc.jsonrpc.handler import JsonRpcRequest, JsonRpcSuccessResult
from modernrpc.xmlrpc.handler import XmlRpcRequest, XmlRpcSuccessResult

if TYPE_CHECKING:
    from modernrpc.types import DictStrAny


@pytest.fixture
def xmlrpc_request() -> str:
    req = """
        <?xml version="1.0"?>
        <methodCall>
          <methodName>foo.bar.baz</methodName>
          <params>
            <param>
              <value>
                <struct>
                  <member>
                    <name>users</name>
                    <value>
                      <array>
                        <data>
                          <value>
                            <struct>
                              <member>
                                <name>_id</name>
                                <value>
                                  <string>684c11581336ab4d790a9db8</string>
                                </value>
                              </member>
                              <member>
                                <name>index</name>
                                <value>
                                  <int>0</int>
                                </value>
                              </member>
                              <member>
                                <name>guid</name>
                                <value>
                                  <string>ce2ac3a3-8b3a-4995-9e89-67fd3f2c0f0f</string>
                                </value>
                              </member>
                              <member>
                                <name>isActive</name>
                                <value>
                                  <boolean>1</boolean>
                                </value>
                              </member>
                              <member>
                                <name>balance</name>
                                <value>
                                  <string>$1,874.14</string>
                                </value>
                              </member>
                              <member>
                                <name>picture</name>
                                <value>
                                  <string>http://placehold.it/32x32</string>
                                </value>
                              </member>
                              <member>
                                <name>age</name>
                                <value>
                                  <int>25</int>
                                </value>
                              </member>
                              <member>
                                <name>eyeColor</name>
                                <value>
                                  <string>brown</string>
                                </value>
                              </member>
                              <member>
                                <name>name</name>
                                <value>
                                  <string>Prince Peck</string>
                                </value>
                              </member>
                              <member>
                                <name>gender</name>
                                <value>
                                  <string>male</string>
                                </value>
                              </member>
                              <member>
                                <name>company</name>
                                <value>
                                  <string>EARWAX</string>
                                </value>
                              </member>
                              <member>
                                <name>email</name>
                                <value>
                                  <string>princepeck@earwax.com</string>
                                </value>
                              </member>
                              <member>
                                <name>phone</name>
                                <value>
                                  <string>+1 (925) 567-3031</string>
                                </value>
                              </member>
                              <member>
                                <name>address</name>
                                <value>
                                  <string>795 Noble Street, Waukeenah, Nevada, 5201</string>
                                </value>
                              </member>
                              <member>
                                <name>about</name>
                                <value>
                                  <string>Officia occaecat cupidatat exercitation amet minim pariatur incididunt sint do qui dolore. Culpa dolor qui sunt excepteur laboris culpa laboris. Anim nostrud qui cillum excepteur incididunt aute eiusmod. Nostrud laborum est elit reprehenderit in nulla eiusmod duis. Laborum ullamco officia irure minim in labore ad occaecat dolor excepteur.</string>
                                </value>
                              </member>
                              <member>
                                <name>registered</name>
                                <value>
                                  <string>2014-05-05T03:15:00 -02:00</string>
                                </value>
                              </member>
                              <member>
                                <name>latitude</name>
                                <value>
                                  <double>87.527037</double>
                                </value>
                              </member>
                              <member>
                                <name>longitude</name>
                                <value>
                                  <double>171.620994</double>
                                </value>
                              </member>
                              <member>
                                <name>tags</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <string>Lorem</string>
                                      </value>
                                      <value>
                                        <string>tempor</string>
                                      </value>
                                      <value>
                                        <string>consequat</string>
                                      </value>
                                      <value>
                                        <string>et</string>
                                      </value>
                                      <value>
                                        <string>nostrud</string>
                                      </value>
                                      <value>
                                        <string>nostrud</string>
                                      </value>
                                      <value>
                                        <string>nostrud</string>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>friends</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>0</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Berry Fox</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>1</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Vonda Oliver</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>2</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Roslyn Abbott</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>greeting</name>
                                <value>
                                  <string>Hello, Prince Peck! You have 2 unread messages.</string>
                                </value>
                              </member>
                              <member>
                                <name>favoriteFruit</name>
                                <value>
                                  <string>apple</string>
                                </value>
                              </member>
                            </struct>
                          </value>
                          <value>
                            <struct>
                              <member>
                                <name>_id</name>
                                <value>
                                  <string>684c11587f643bdfe2960b12</string>
                                </value>
                              </member>
                              <member>
                                <name>index</name>
                                <value>
                                  <int>1</int>
                                </value>
                              </member>
                              <member>
                                <name>guid</name>
                                <value>
                                  <string>1913e9f5-6316-4d52-8063-c2f5664b8115</string>
                                </value>
                              </member>
                              <member>
                                <name>isActive</name>
                                <value>
                                  <boolean>0</boolean>
                                </value>
                              </member>
                              <member>
                                <name>balance</name>
                                <value>
                                  <string>$2,993.90</string>
                                </value>
                              </member>
                              <member>
                                <name>picture</name>
                                <value>
                                  <string>http://placehold.it/32x32</string>
                                </value>
                              </member>
                              <member>
                                <name>age</name>
                                <value>
                                  <int>30</int>
                                </value>
                              </member>
                              <member>
                                <name>eyeColor</name>
                                <value>
                                  <string>green</string>
                                </value>
                              </member>
                              <member>
                                <name>name</name>
                                <value>
                                  <string>Rosalyn Mayo</string>
                                </value>
                              </member>
                              <member>
                                <name>gender</name>
                                <value>
                                  <string>female</string>
                                </value>
                              </member>
                              <member>
                                <name>company</name>
                                <value>
                                  <string>DOGNOST</string>
                                </value>
                              </member>
                              <member>
                                <name>email</name>
                                <value>
                                  <string>rosalynmayo@dognost.com</string>
                                </value>
                              </member>
                              <member>
                                <name>phone</name>
                                <value>
                                  <string>+1 (975) 469-2169</string>
                                </value>
                              </member>
                              <member>
                                <name>address</name>
                                <value>
                                  <string>582 Moffat Street, Connerton, Ohio, 2966</string>
                                </value>
                              </member>
                              <member>
                                <name>about</name>
                                <value>
                                  <string>Eu ullamco id consectetur non ipsum. Lorem commodo ex ut nulla. Officia in dolore nulla reprehenderit Lorem enim id non commodo quis aliqua consequat pariatur. Laboris reprehenderit veniam cupidatat occaecat pariatur deserunt tempor ullamco minim laboris.</string>
                                </value>
                              </member>
                              <member>
                                <name>registered</name>
                                <value>
                                  <string>2025-05-22T05:43:48 -02:00</string>
                                </value>
                              </member>
                              <member>
                                <name>latitude</name>
                                <value>
                                  <double>-56.066359</double>
                                </value>
                              </member>
                              <member>
                                <name>longitude</name>
                                <value>
                                  <double>49.021658</double>
                                </value>
                              </member>
                              <member>
                                <name>tags</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <string>aliqua</string>
                                      </value>
                                      <value>
                                        <string>veniam</string>
                                      </value>
                                      <value>
                                        <string>qui</string>
                                      </value>
                                      <value>
                                        <string>et</string>
                                      </value>
                                      <value>
                                        <string>dolore</string>
                                      </value>
                                      <value>
                                        <string>reprehenderit</string>
                                      </value>
                                      <value>
                                        <string>anim</string>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>friends</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>0</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Benjamin Farley</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>1</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Wilkins Lindsay</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>2</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Sharp Booker</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>greeting</name>
                                <value>
                                  <string>Hello, Rosalyn Mayo! You have 4 unread messages.</string>
                                </value>
                              </member>
                              <member>
                                <name>favoriteFruit</name>
                                <value>
                                  <string>strawberry</string>
                                </value>
                              </member>
                            </struct>
                          </value>
                          <value>
                            <struct>
                              <member>
                                <name>_id</name>
                                <value>
                                  <string>684c1158e2da5612edaf89bc</string>
                                </value>
                              </member>
                              <member>
                                <name>index</name>
                                <value>
                                  <int>2</int>
                                </value>
                              </member>
                              <member>
                                <name>guid</name>
                                <value>
                                  <string>f35a5510-913f-4361-8db4-cd3387a7ba23</string>
                                </value>
                              </member>
                              <member>
                                <name>isActive</name>
                                <value>
                                  <boolean>1</boolean>
                                </value>
                              </member>
                              <member>
                                <name>balance</name>
                                <value>
                                  <string>$2,113.81</string>
                                </value>
                              </member>
                              <member>
                                <name>picture</name>
                                <value>
                                  <string>http://placehold.it/32x32</string>
                                </value>
                              </member>
                              <member>
                                <name>age</name>
                                <value>
                                  <int>28</int>
                                </value>
                              </member>
                              <member>
                                <name>eyeColor</name>
                                <value>
                                  <string>brown</string>
                                </value>
                              </member>
                              <member>
                                <name>name</name>
                                <value>
                                  <string>Lottie David</string>
                                </value>
                              </member>
                              <member>
                                <name>gender</name>
                                <value>
                                  <string>female</string>
                                </value>
                              </member>
                              <member>
                                <name>company</name>
                                <value>
                                  <string>SHEPARD</string>
                                </value>
                              </member>
                              <member>
                                <name>email</name>
                                <value>
                                  <string>lottiedavid@shepard.com</string>
                                </value>
                              </member>
                              <member>
                                <name>phone</name>
                                <value>
                                  <string>+1 (828) 577-2869</string>
                                </value>
                              </member>
                              <member>
                                <name>address</name>
                                <value>
                                  <string>677 Berriman Street, Wadsworth, Alaska, 9975</string>
                                </value>
                              </member>
                              <member>
                                <name>about</name>
                                <value>
                                  <string>Velit ad nisi nostrud ipsum non dolore exercitation eiusmod. Veniam minim sint officia sit cupidatat dolore consectetur in do cupidatat eu ullamco. Aliquip in ullamco amet consectetur deserunt incididunt enim qui ullamco dolor non dolor et. Deserunt nisi sit est est fugiat id. Incididunt ipsum eiusmod aute incididunt amet quis commodo in et veniam nostrud dolore.</string>
                                </value>
                              </member>
                              <member>
                                <name>registered</name>
                                <value>
                                  <string>2016-03-28T10:27:06 -02:00</string>
                                </value>
                              </member>
                              <member>
                                <name>latitude</name>
                                <value>
                                  <double>-22.067648</double>
                                </value>
                              </member>
                              <member>
                                <name>longitude</name>
                                <value>
                                  <double>-43.543746</double>
                                </value>
                              </member>
                              <member>
                                <name>tags</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <string>ut</string>
                                      </value>
                                      <value>
                                        <string>in</string>
                                      </value>
                                      <value>
                                        <string>qui</string>
                                      </value>
                                      <value>
                                        <string>velit</string>
                                      </value>
                                      <value>
                                        <string>elit</string>
                                      </value>
                                      <value>
                                        <string>est</string>
                                      </value>
                                      <value>
                                        <string>nostrud</string>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>friends</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>0</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Casandra Rasmussen</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>1</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Leah Donovan</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>2</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Griffin Cline</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>greeting</name>
                                <value>
                                  <string>Hello, Lottie David! You have 9 unread messages.</string>
                                </value>
                              </member>
                              <member>
                                <name>favoriteFruit</name>
                                <value>
                                  <string>apple</string>
                                </value>
                              </member>
                            </struct>
                          </value>
                          <value>
                            <struct>
                              <member>
                                <name>_id</name>
                                <value>
                                  <string>684c1158968c1f46c88a2576</string>
                                </value>
                              </member>
                              <member>
                                <name>index</name>
                                <value>
                                  <int>3</int>
                                </value>
                              </member>
                              <member>
                                <name>guid</name>
                                <value>
                                  <string>9fd20e98-74fd-4061-8e45-6576d58dad3e</string>
                                </value>
                              </member>
                              <member>
                                <name>isActive</name>
                                <value>
                                  <boolean>1</boolean>
                                </value>
                              </member>
                              <member>
                                <name>balance</name>
                                <value>
                                  <string>$3,623.99</string>
                                </value>
                              </member>
                              <member>
                                <name>picture</name>
                                <value>
                                  <string>http://placehold.it/32x32</string>
                                </value>
                              </member>
                              <member>
                                <name>age</name>
                                <value>
                                  <int>31</int>
                                </value>
                              </member>
                              <member>
                                <name>eyeColor</name>
                                <value>
                                  <string>blue</string>
                                </value>
                              </member>
                              <member>
                                <name>name</name>
                                <value>
                                  <string>Lancaster Gardner</string>
                                </value>
                              </member>
                              <member>
                                <name>gender</name>
                                <value>
                                  <string>male</string>
                                </value>
                              </member>
                              <member>
                                <name>company</name>
                                <value>
                                  <string>WAZZU</string>
                                </value>
                              </member>
                              <member>
                                <name>email</name>
                                <value>
                                  <string>lancastergardner@wazzu.com</string>
                                </value>
                              </member>
                              <member>
                                <name>phone</name>
                                <value>
                                  <string>+1 (881) 511-3948</string>
                                </value>
                              </member>
                              <member>
                                <name>address</name>
                                <value>
                                  <string>722 Mill Road, Madrid, Federated States Of Micronesia, 3120</string>
                                </value>
                              </member>
                              <member>
                                <name>about</name>
                                <value>
                                  <string>Irure velit ex labore eiusmod velit irure do minim voluptate excepteur ullamco. Nisi Lorem ut irure duis esse do excepteur excepteur fugiat officia elit. Deserunt et mollit eiusmod sit occaecat culpa eu consequat aliqua ad mollit et aliquip consectetur.</string>
                                </value>
                              </member>
                              <member>
                                <name>registered</name>
                                <value>
                                  <string>2024-12-06T06:55:45 -01:00</string>
                                </value>
                              </member>
                              <member>
                                <name>latitude</name>
                                <value>
                                  <double>-50.108538</double>
                                </value>
                              </member>
                              <member>
                                <name>longitude</name>
                                <value>
                                  <double>103.6506</double>
                                </value>
                              </member>
                              <member>
                                <name>tags</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <string>proident</string>
                                      </value>
                                      <value>
                                        <string>adipisicing</string>
                                      </value>
                                      <value>
                                        <string>in</string>
                                      </value>
                                      <value>
                                        <string>do</string>
                                      </value>
                                      <value>
                                        <string>quis</string>
                                      </value>
                                      <value>
                                        <string>officia</string>
                                      </value>
                                      <value>
                                        <string>occaecat</string>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>friends</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>0</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Sheri Sosa</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>1</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Graves Whitehead</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>2</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Selma Murphy</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>greeting</name>
                                <value>
                                  <string>Hello, Lancaster Gardner! You have 4 unread messages.</string>
                                </value>
                              </member>
                              <member>
                                <name>favoriteFruit</name>
                                <value>
                                  <string>strawberry</string>
                                </value>
                              </member>
                            </struct>
                          </value>
                          <value>
                            <struct>
                              <member>
                                <name>_id</name>
                                <value>
                                  <string>684c1158c52b47c4b74b53e1</string>
                                </value>
                              </member>
                              <member>
                                <name>index</name>
                                <value>
                                  <int>4</int>
                                </value>
                              </member>
                              <member>
                                <name>guid</name>
                                <value>
                                  <string>2b00b3f8-3690-43ad-9e52-b5a8da03b033</string>
                                </value>
                              </member>
                              <member>
                                <name>isActive</name>
                                <value>
                                  <boolean>0</boolean>
                                </value>
                              </member>
                              <member>
                                <name>balance</name>
                                <value>
                                  <string>$3,263.00</string>
                                </value>
                              </member>
                              <member>
                                <name>picture</name>
                                <value>
                                  <string>http://placehold.it/32x32</string>
                                </value>
                              </member>
                              <member>
                                <name>age</name>
                                <value>
                                  <int>23</int>
                                </value>
                              </member>
                              <member>
                                <name>eyeColor</name>
                                <value>
                                  <string>blue</string>
                                </value>
                              </member>
                              <member>
                                <name>name</name>
                                <value>
                                  <string>Hope Hernandez</string>
                                </value>
                              </member>
                              <member>
                                <name>gender</name>
                                <value>
                                  <string>female</string>
                                </value>
                              </member>
                              <member>
                                <name>company</name>
                                <value>
                                  <string>TUBESYS</string>
                                </value>
                              </member>
                              <member>
                                <name>email</name>
                                <value>
                                  <string>hopehernandez@tubesys.com</string>
                                </value>
                              </member>
                              <member>
                                <name>phone</name>
                                <value>
                                  <string>+1 (906) 441-2779</string>
                                </value>
                              </member>
                              <member>
                                <name>address</name>
                                <value>
                                  <string>524 Court Square, Echo, South Dakota, 6518</string>
                                </value>
                              </member>
                              <member>
                                <name>about</name>
                                <value>
                                  <string>Labore esse occaecat occaecat ut ullamco adipisicing nisi mollit. Quis tempor non pariatur id ex ex. Sit ea enim Lorem reprehenderit magna culpa laboris ipsum reprehenderit. Fugiat deserunt ad adipisicing reprehenderit quis est nostrud nostrud mollit ad.</string>
                                </value>
                              </member>
                              <member>
                                <name>registered</name>
                                <value>
                                  <string>2023-12-12T05:33:01 -01:00</string>
                                </value>
                              </member>
                              <member>
                                <name>latitude</name>
                                <value>
                                  <double>-87.316379</double>
                                </value>
                              </member>
                              <member>
                                <name>longitude</name>
                                <value>
                                  <double>-71.37343</double>
                                </value>
                              </member>
                              <member>
                                <name>tags</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <string>sit</string>
                                      </value>
                                      <value>
                                        <string>deserunt</string>
                                      </value>
                                      <value>
                                        <string>reprehenderit</string>
                                      </value>
                                      <value>
                                        <string>reprehenderit</string>
                                      </value>
                                      <value>
                                        <string>do</string>
                                      </value>
                                      <value>
                                        <string>cillum</string>
                                      </value>
                                      <value>
                                        <string>et</string>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>friends</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>0</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Beryl Tucker</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>1</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Adriana Rosa</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>id</name>
                                            <value>
                                              <int>2</int>
                                            </value>
                                          </member>
                                          <member>
                                            <name>name</name>
                                            <value>
                                              <string>Vilma Chapman</string>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>greeting</name>
                                <value>
                                  <string>Hello, Hope Hernandez! You have 8 unread messages.</string>
                                </value>
                              </member>
                              <member>
                                <name>favoriteFruit</name>
                                <value>
                                  <string>apple</string>
                                </value>
                              </member>
                            </struct>
                          </value>
                        </data>
                      </array>
                    </value>
                  </member>
                  <member>
                    <name>history</name>
                    <value>
                      <array>
                        <data>
                          <value>
                            <struct>
                              <member>
                                <name>message</name>
                                <value>
                                  <string>Hello, Joanne! Your order number is: #40</string>
                                </value>
                              </member>
                              <member>
                                <name>phoneNumber</name>
                                <value>
                                  <string>257-209-5208 x31724</string>
                                </value>
                              </member>
                              <member>
                                <name>phoneVariation</name>
                                <value>
                                  <string>+90 304 309 10 49</string>
                                </value>
                              </member>
                              <member>
                                <name>status</name>
                                <value>
                                  <string>active</string>
                                </value>
                              </member>
                              <member>
                                <name>name</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>first</name>
                                      <value>
                                        <string>Kane</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>middle</name>
                                      <value>
                                        <string>Shawn</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>last</name>
                                      <value>
                                        <string>Padberg</string>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>username</name>
                                <value>
                                  <string>Kane-Padberg</string>
                                </value>
                              </member>
                              <member>
                                <name>password</name>
                                <value>
                                  <string>dcim2pc7ObdOZIX</string>
                                </value>
                              </member>
                              <member>
                                <name>emails</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <string>Cory5@example.com</string>
                                      </value>
                                      <value>
                                        <string>Carson.Dickens24@example.com</string>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>location</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>street</name>
                                      <value>
                                        <string>8691 S High Street</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>city</name>
                                      <value>
                                        <string>Pontiac</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>state</name>
                                      <value>
                                        <string>Maryland</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>country</name>
                                      <value>
                                        <string>Jersey</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>zip</name>
                                      <value>
                                        <string>46308</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>coordinates</name>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>latitude</name>
                                            <value>
                                              <double>-61.8787</double>
                                            </value>
                                          </member>
                                          <member>
                                            <name>longitude</name>
                                            <value>
                                              <double>-139.3919</double>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>website</name>
                                <value>
                                  <string>https://fine-ruby.biz/</string>
                                </value>
                              </member>
                              <member>
                                <name>domain</name>
                                <value>
                                  <string>irresponsible-elbow.com</string>
                                </value>
                              </member>
                              <member>
                                <name>job</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>title</name>
                                      <value>
                                        <string>Product Factors Director</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>descriptor</name>
                                      <value>
                                        <string>Legacy</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>area</name>
                                      <value>
                                        <string>Brand</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>type</name>
                                      <value>
                                        <string>Coordinator</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>company</name>
                                      <value>
                                        <string>Ward, Hoeger and Harris</string>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>creditCard</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>number</name>
                                      <value>
                                        <string>6470-6222-3990-2886-2848</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>cvv</name>
                                      <value>
                                        <int>462</int>
                                      </value>
                                    </member>
                                    <member>
                                      <name>issuer</name>
                                      <value>
                                        <string>mastercard</string>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>uuid</name>
                                <value>
                                  <string>37e2c28f-f94c-45fa-804f-d93621788997</string>
                                </value>
                              </member>
                              <member>
                                <name>objectId</name>
                                <value>
                                  <string>684c18ff84045dc1f0bc8830</string>
                                </value>
                              </member>
                            </struct>
                          </value>
                          <value>
                            <struct>
                              <member>
                                <name>message</name>
                                <value>
                                  <string>Hello, Jonas! Your order number is: #93</string>
                                </value>
                              </member>
                              <member>
                                <name>phoneNumber</name>
                                <value>
                                  <string>281.690.2763 x578</string>
                                </value>
                              </member>
                              <member>
                                <name>phoneVariation</name>
                                <value>
                                  <string>+90 384 815 10 81</string>
                                </value>
                              </member>
                              <member>
                                <name>status</name>
                                <value>
                                  <string>active</string>
                                </value>
                              </member>
                              <member>
                                <name>name</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>first</name>
                                      <value>
                                        <string>Zack</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>middle</name>
                                      <value>
                                        <string>Jamie</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>last</name>
                                      <value>
                                        <string>Stroman</string>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>username</name>
                                <value>
                                  <string>Zack-Stroman</string>
                                </value>
                              </member>
                              <member>
                                <name>password</name>
                                <value>
                                  <string>rLGJOmstq1cmWgO</string>
                                </value>
                              </member>
                              <member>
                                <name>emails</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <string>Glenna_Nicolas99@example.com</string>
                                      </value>
                                      <value>
                                        <string>Hildegard.Denesik@gmail.com</string>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>location</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>street</name>
                                      <value>
                                        <string>29801 Haley Skyway</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>city</name>
                                      <value>
                                        <string>North Javierberg</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>state</name>
                                      <value>
                                        <string>Nevada</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>country</name>
                                      <value>
                                        <string>Dominican Republic</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>zip</name>
                                      <value>
                                        <string>56777-2825</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>coordinates</name>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>latitude</name>
                                            <value>
                                              <double>85.9856</double>
                                            </value>
                                          </member>
                                          <member>
                                            <name>longitude</name>
                                            <value>
                                              <double>-100.7706</double>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>website</name>
                                <value>
                                  <string>https://massive-change.name/</string>
                                </value>
                              </member>
                              <member>
                                <name>domain</name>
                                <value>
                                  <string>forsaken-sorbet.info</string>
                                </value>
                              </member>
                              <member>
                                <name>job</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>title</name>
                                      <value>
                                        <string>District Creative Developer</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>descriptor</name>
                                      <value>
                                        <string>Customer</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>area</name>
                                      <value>
                                        <string>Operations</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>type</name>
                                      <value>
                                        <string>Architect</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>company</name>
                                      <value>
                                        <string>Mann, Ortiz and Moen</string>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>creditCard</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>number</name>
                                      <value>
                                        <string>2301-2383-4501-2072</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>cvv</name>
                                      <value>
                                        <int>757</int>
                                      </value>
                                    </member>
                                    <member>
                                      <name>issuer</name>
                                      <value>
                                        <string>mastercard</string>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>uuid</name>
                                <value>
                                  <string>c59d2b43-f75f-449b-b5ac-88cbbfab347f</string>
                                </value>
                              </member>
                              <member>
                                <name>objectId</name>
                                <value>
                                  <string>684c18ff84045dc1f0bc8831</string>
                                </value>
                              </member>
                            </struct>
                          </value>
                          <value>
                            <struct>
                              <member>
                                <name>message</name>
                                <value>
                                  <string>Hello, Carlo! Your order number is: #62</string>
                                </value>
                              </member>
                              <member>
                                <name>phoneNumber</name>
                                <value>
                                  <string>(391) 215-2767</string>
                                </value>
                              </member>
                              <member>
                                <name>phoneVariation</name>
                                <value>
                                  <string>+90 342 215 10 64</string>
                                </value>
                              </member>
                              <member>
                                <name>status</name>
                                <value>
                                  <string>active</string>
                                </value>
                              </member>
                              <member>
                                <name>name</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>first</name>
                                      <value>
                                        <string>Kiara</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>middle</name>
                                      <value>
                                        <string>Billie</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>last</name>
                                      <value>
                                        <string>Schneider</string>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>username</name>
                                <value>
                                  <string>Kiara-Schneider</string>
                                </value>
                              </member>
                              <member>
                                <name>password</name>
                                <value>
                                  <string>HOiJvKaiojXhHPU</string>
                                </value>
                              </member>
                              <member>
                                <name>emails</name>
                                <value>
                                  <array>
                                    <data>
                                      <value>
                                        <string>Elyse.Bernier@example.com</string>
                                      </value>
                                      <value>
                                        <string>Jackeline85@example.com</string>
                                      </value>
                                    </data>
                                  </array>
                                </value>
                              </member>
                              <member>
                                <name>location</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>street</name>
                                      <value>
                                        <string>4927 Pfannerstill Glens</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>city</name>
                                      <value>
                                        <string>Jefferson City</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>state</name>
                                      <value>
                                        <string>Ohio</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>country</name>
                                      <value>
                                        <string>Tuvalu</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>zip</name>
                                      <value>
                                        <string>78191-9058</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>coordinates</name>
                                      <value>
                                        <struct>
                                          <member>
                                            <name>latitude</name>
                                            <value>
                                              <double>-14.9516</double>
                                            </value>
                                          </member>
                                          <member>
                                            <name>longitude</name>
                                            <value>
                                              <double>-19.1723</double>
                                            </value>
                                          </member>
                                        </struct>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>website</name>
                                <value>
                                  <string>https://colossal-mastication.name/</string>
                                </value>
                              </member>
                              <member>
                                <name>domain</name>
                                <value>
                                  <string>ashamed-sword.net</string>
                                </value>
                              </member>
                              <member>
                                <name>job</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>title</name>
                                      <value>
                                        <string>Dynamic Metrics Strategist</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>descriptor</name>
                                      <value>
                                        <string>Legacy</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>area</name>
                                      <value>
                                        <string>Brand</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>type</name>
                                      <value>
                                        <string>Supervisor</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>company</name>
                                      <value>
                                        <string>Simonis, Boehm and Price</string>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>creditCard</name>
                                <value>
                                  <struct>
                                    <member>
                                      <name>number</name>
                                      <value>
                                        <string>3588-8488-6973-8282</string>
                                      </value>
                                    </member>
                                    <member>
                                      <name>cvv</name>
                                      <value>
                                        <int>796</int>
                                      </value>
                                    </member>
                                    <member>
                                      <name>issuer</name>
                                      <value>
                                        <string>visa</string>
                                      </value>
                                    </member>
                                  </struct>
                                </value>
                              </member>
                              <member>
                                <name>uuid</name>
                                <value>
                                  <string>80110005-8b23-4829-a383-9e62f3d7b7a0</string>
                                </value>
                              </member>
                              <member>
                                <name>objectId</name>
                                <value>
                                  <string>684c18ff84045dc1f0bc8832</string>
                                </value>
                              </member>
                            </struct>
                          </value>
                        </data>
                      </array>
                    </value>
                  </member>
                </struct>
              </value>
            </param>
          </params>
        </methodCall>
    """  # noqa: E501 (long lines are acceptable here)
    return dedent(req).lstrip()


@pytest.fixture(scope="session")
def random_data() -> DictStrAny:
    return {
        "users": [
            {
                "_id": "684c11581336ab4d790a9db8",
                "index": 0,
                "guid": "ce2ac3a3-8b3a-4995-9e89-67fd3f2c0f0f",
                "isActive": True,
                "balance": "$1,874.14",
                "picture": "http://placehold.it/32x32",
                "age": 25,
                "eyeColor": "brown",
                "name": "Prince Peck",
                "gender": "male",
                "company": "EARWAX",
                "email": "princepeck@earwax.com",
                "phone": "+1 (925) 567-3031",
                "address": "795 Noble Street, Waukeenah, Nevada, 5201",
                "about": "Officia occaecat cupidatat exercitation amet minim pariatur incididunt sint do "
                "qui dolore. Culpa dolor qui sunt excepteur laboris culpa laboris. Anim nostrud "
                "qui cillum excepteur incididunt aute eiusmod. Nostrud laborum est elit reprehenderit "
                "in nulla eiusmod duis. Laborum ullamco officia irure minim in labore ad occaecat "
                "dolor excepteur.",
                "registered": "2014-05-05T03:15:00 -02:00",
                "latitude": 87.527037,
                "longitude": 171.620994,
                "tags": ["Lorem", "tempor", "consequat", "et", "nostrud", "nostrud", "nostrud"],
                "friends": [
                    {"id": 0, "name": "Berry Fox"},
                    {"id": 1, "name": "Vonda Oliver"},
                    {"id": 2, "name": "Roslyn Abbott"},
                ],
                "greeting": "Hello, Prince Peck! You have 2 unread messages.",
                "favoriteFruit": "apple",
            },
            {
                "_id": "684c11587f643bdfe2960b12",
                "index": 1,
                "guid": "1913e9f5-6316-4d52-8063-c2f5664b8115",
                "isActive": False,
                "balance": "$2,993.90",
                "picture": "http://placehold.it/32x32",
                "age": 30,
                "eyeColor": "green",
                "name": "Rosalyn Mayo",
                "gender": "female",
                "company": "DOGNOST",
                "email": "rosalynmayo@dognost.com",
                "phone": "+1 (975) 469-2169",
                "address": "582 Moffat Street, Connerton, Ohio, 2966",
                "about": "Eu ullamco id consectetur non ipsum. Lorem commodo ex ut nulla. Officia in dolore "
                "nulla reprehenderit Lorem enim id non commodo quis aliqua consequat pariatur. Laboris "
                "reprehenderit veniam cupidatat occaecat pariatur deserunt tempor ullamco minim laboris.",
                "registered": "2025-05-22T05:43:48 -02:00",
                "latitude": -56.066359,
                "longitude": 49.021658,
                "tags": ["aliqua", "veniam", "qui", "et", "dolore", "reprehenderit", "anim"],
                "friends": [
                    {"id": 0, "name": "Benjamin Farley"},
                    {"id": 1, "name": "Wilkins Lindsay"},
                    {"id": 2, "name": "Sharp Booker"},
                ],
                "greeting": "Hello, Rosalyn Mayo! You have 4 unread messages.",
                "favoriteFruit": "strawberry",
            },
            {
                "_id": "684c1158e2da5612edaf89bc",
                "index": 2,
                "guid": "f35a5510-913f-4361-8db4-cd3387a7ba23",
                "isActive": True,
                "balance": "$2,113.81",
                "picture": "http://placehold.it/32x32",
                "age": 28,
                "eyeColor": "brown",
                "name": "Lottie David",
                "gender": "female",
                "company": "SHEPARD",
                "email": "lottiedavid@shepard.com",
                "phone": "+1 (828) 577-2869",
                "address": "677 Berriman Street, Wadsworth, Alaska, 9975",
                "about": "Velit ad nisi nostrud ipsum non dolore exercitation eiusmod. Veniam minim sint officia sit "
                "cupidatat dolore consectetur in do cupidatat eu ullamco. Aliquip in ullamco amet consectetur "
                "deserunt incididunt enim qui ullamco dolor non dolor et. Deserunt nisi sit est est fugiat "
                "id. Incididunt ipsum eiusmod aute incididunt amet quis commodo in et veniam nostrud dolore.",
                "registered": "2016-03-28T10:27:06 -02:00",
                "latitude": -22.067648,
                "longitude": -43.543746,
                "tags": ["ut", "in", "qui", "velit", "elit", "est", "nostrud"],
                "friends": [
                    {"id": 0, "name": "Casandra Rasmussen"},
                    {"id": 1, "name": "Leah Donovan"},
                    {"id": 2, "name": "Griffin Cline"},
                ],
                "greeting": "Hello, Lottie David! You have 9 unread messages.",
                "favoriteFruit": "apple",
            },
            {
                "_id": "684c1158968c1f46c88a2576",
                "index": 3,
                "guid": "9fd20e98-74fd-4061-8e45-6576d58dad3e",
                "isActive": True,
                "balance": "$3,623.99",
                "picture": "http://placehold.it/32x32",
                "age": 31,
                "eyeColor": "blue",
                "name": "Lancaster Gardner",
                "gender": "male",
                "company": "WAZZU",
                "email": "lancastergardner@wazzu.com",
                "phone": "+1 (881) 511-3948",
                "address": "722 Mill Road, Madrid, Federated States Of Micronesia, 3120",
                "about": "Irure velit ex labore eiusmod velit irure do minim voluptate excepteur ullamco. Nisi Lorem "
                "ut irure duis esse do excepteur excepteur fugiat officia elit. Deserunt et mollit eiusmod "
                "sit occaecat culpa eu consequat aliqua ad mollit et aliquip consectetur.",
                "registered": "2024-12-06T06:55:45 -01:00",
                "latitude": -50.108538,
                "longitude": 103.6506,
                "tags": ["proident", "adipisicing", "in", "do", "quis", "officia", "occaecat"],
                "friends": [
                    {"id": 0, "name": "Sheri Sosa"},
                    {"id": 1, "name": "Graves Whitehead"},
                    {"id": 2, "name": "Selma Murphy"},
                ],
                "greeting": "Hello, Lancaster Gardner! You have 4 unread messages.",
                "favoriteFruit": "strawberry",
            },
            {
                "_id": "684c1158c52b47c4b74b53e1",
                "index": 4,
                "guid": "2b00b3f8-3690-43ad-9e52-b5a8da03b033",
                "isActive": False,
                "balance": "$3,263.00",
                "picture": "http://placehold.it/32x32",
                "age": 23,
                "eyeColor": "blue",
                "name": "Hope Hernandez",
                "gender": "female",
                "company": "TUBESYS",
                "email": "hopehernandez@tubesys.com",
                "phone": "+1 (906) 441-2779",
                "address": "524 Court Square, Echo, South Dakota, 6518",
                "about": "Labore esse occaecat occaecat ut ullamco adipisicing nisi mollit. Quis tempor non pariatur "
                "id ex ex. Sit ea enim Lorem reprehenderit magna culpa laboris ipsum reprehenderit. Fugiat "
                "deserunt ad adipisicing reprehenderit quis est nostrud nostrud mollit ad.",
                "registered": "2023-12-12T05:33:01 -01:00",
                "latitude": -87.316379,
                "longitude": -71.37343,
                "tags": ["sit", "deserunt", "reprehenderit", "reprehenderit", "do", "cillum", "et"],
                "friends": [
                    {"id": 0, "name": "Beryl Tucker"},
                    {"id": 1, "name": "Adriana Rosa"},
                    {"id": 2, "name": "Vilma Chapman"},
                ],
                "greeting": "Hello, Hope Hernandez! You have 8 unread messages.",
                "favoriteFruit": "apple",
            },
        ],
        "history": [
            {
                "message": "Hello, Joanne! Your order number is: #40",
                "phoneNumber": "257-209-5208 x31724",
                "phoneVariation": "+90 304 309 10 49",
                "status": "active",
                "name": {"first": "Kane", "middle": "Shawn", "last": "Padberg"},
                "username": "Kane-Padberg",
                "auth_kkk": "dcim2pc7ObdOZIX",
                "emails": ["Cory5@example.com", "Carson.Dickens24@example.com"],
                "location": {
                    "street": "8691 S High Street",
                    "city": "Pontiac",
                    "state": "Maryland",
                    "country": "Jersey",
                    "zip": "46308",
                    "coordinates": {"latitude": -61.8787, "longitude": -139.3919},
                },
                "website": "https://fine-ruby.biz/",
                "domain": "irresponsible-elbow.com",
                "job": {
                    "title": "Product Factors Director",
                    "descriptor": "Legacy",
                    "area": "Brand",
                    "type": "Coordinator",
                    "company": "Ward, Hoeger and Harris",
                },
                "creditCard": {"number": "6470-6222-3990-2886-2848", "cvv": 462, "issuer": "mastercard"},
                "uuid": "37e2c28f-f94c-45fa-804f-d93621788997",
                "objectId": "684c18ff84045dc1f0bc8830",
            },
            {
                "message": "Hello, Jonas! Your order number is: #93",
                "phoneNumber": "281.690.2763 x578",
                "phoneVariation": "+90 384 815 10 81",
                "status": "active",
                "name": {"first": "Zack", "middle": "Jamie", "last": "Stroman"},
                "username": "Zack-Stroman",
                "another_value": "rLGJOmstq1cmWgO",
                "emails": ["Glenna_Nicolas99@example.com", "Hildegard.Denesik@gmail.com"],
                "location": {
                    "street": "29801 Haley Skyway",
                    "city": "North Javierberg",
                    "state": "Nevada",
                    "country": "Dominican Republic",
                    "zip": "56777-2825",
                    "coordinates": {"latitude": 85.9856, "longitude": -100.7706},
                },
                "website": "https://massive-change.name/",
                "domain": "forsaken-sorbet.info",
                "job": {
                    "title": "District Creative Developer",
                    "descriptor": "Customer",
                    "area": "Operations",
                    "type": "Architect",
                    "company": "Mann, Ortiz and Moen",
                },
                "creditCard": {"number": "2301-2383-4501-2072", "cvv": 757, "issuer": "mastercard"},
                "uuid": "c59d2b43-f75f-449b-b5ac-88cbbfab347f",
                "objectId": "684c18ff84045dc1f0bc8831",
            },
            {
                "message": "Hello, Carlo! Your order number is: #62",
                "phoneNumber": "(391) 215-2767",
                "phoneVariation": "+90 342 215 10 64",
                "status": "active",
                "name": {"first": "Kiara", "middle": "Billie", "last": "Schneider"},
                "username": "Kiara-Schneider",
                "emails": ["Elyse.Bernier@example.com", "Jackeline85@example.com"],
                "location": {
                    "street": "4927 Pfannerstill Glens",
                    "city": "Jefferson City",
                    "state": "Ohio",
                    "country": "Tuvalu",
                    "zip": "78191-9058",
                    "coordinates": {"latitude": -14.9516, "longitude": -19.1723},
                },
                "website": "https://colossal-mastication.name/",
                "domain": "ashamed-sword.net",
                "job": {
                    "title": "Dynamic Metrics Strategist",
                    "descriptor": "Legacy",
                    "area": "Brand",
                    "type": "Supervisor",
                    "company": "Simonis, Boehm and Price",
                },
                "creditCard": {"number": "3588-8488-6973-8282", "cvv": 796, "issuer": "visa"},
                "uuid": "80110005-8b23-4829-a383-9e62f3d7b7a0",
                "objectId": "684c18ff84045dc1f0bc8832",
            },
        ],
    }


@pytest.fixture
def jsonrpc_request(random_data) -> str:
    req = """
        {
          "id": 255,
          "jsonrpc": "2.0",
          "method": "foo",
          "params": %s
        }
    """ % json.dumps(random_data, indent=2)  # noqa: UP031 (str formatting is better when building a json payload)
    return dedent(req)


@pytest.fixture
def jsonrpc_result(random_data) -> JsonRpcSuccessResult:
    return JsonRpcSuccessResult(request=JsonRpcRequest(request_id=500, method_name=""), data=random_data)


@pytest.fixture
def xmlrpc_result(random_data) -> XmlRpcSuccessResult:
    return XmlRpcSuccessResult(request=XmlRpcRequest(method_name=""), data=random_data)
