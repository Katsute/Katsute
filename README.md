<div align="center">
    <img 
        src="https://img.shields.io/badge/OS-Windows-informational?style=for-the-badge&color=3278be"
        alt="Windows-OS">
    <img 
        src="https://img.shields.io/github/followers/katsute?color=3278be&style=for-the-badge"
        alt="followers">
</div>

<hr>

## ⭐ Information

 - Currently majoring in Computer Information Systems (CIS) at Baruch College

## 🔧 Technologies & Tools

<img 
    src="https://img.shields.io/badge/OS-Windows-informational?style=flat-square&color=3278be"
    alt="Windows-OS">
<img 
    src="https://img.shields.io/badge/Editor-IntelliJ_IDEA-informational?style=flat-square&logo=intellij-idea&logoColor=white&color=3278be"
    alt="IntelliJ-IDE">
<img 
    src="https://img.shields.io/badge/Editor-Visual_Studio_Code-informational?style=flat-square&logo=Visual-Studio-Code&logoColor=white&color=3278be"
    alt="Visual-Studio-Code-IDE">
<img 
    src="https://img.shields.io/badge/Code-Java-informational?style=flat-square&logo=java&logoColor=white&color=3278be"
    alt="Java">
<img 
    src="https://img.shields.io/badge/Code-HTML-informational?style=flat-square&logo=html5&logoColor=white&color=3278be"
    alt="HTML">
<img 
    src="https://img.shields.io/badge/Code-CSS-informational?style=flat-square&logo=css-wizardry&logoColor=white&color=3278be"
    alt="CSS">
<img 
    src="https://img.shields.io/badge/Code-SASS-informational?style=flat-square&logo=sass&logoColor=white&color=3278be"
    alt="SASS">
<img 
    src="https://img.shields.io/badge/Code-JavaScript-informational?style=flat-square&logo=javascript&logoColor=white&color=3278be"
    alt="JavaScript">
<img 
    src="https://img.shields.io/badge/Tools-Maven-informational?style=flat-square&logo=apache-maven&logoColor=white&color=3278be"
    alt="Maven">

## 📊 Statistics
<div align="center">
    <a href="https://github.com/Katsute/Katsute/">
        <img src="https://github.com/Katsute/Katsute/blob/master/contributions.png">
    </a>
    <a href="https://github.com/Katsute/Katsute/">
        <img src="https://github.com/Katsute/Katsute/blob/master/languages.png">
    </a>
</div>

## 👨‍💻 Repositories Being Worked On Currently
<div align="center">
    <a href="https://github.com/Ktt-Development/ktt-development.github.io">
        <img
            src="https://github-readme-stats.vercel.app/api/pin/?username=ktt-development&repo=ktt-development.github.io&show_owner=true&title_color=3278be&text_color=202020">
    </a>
    <a href="https://github.com/Ktt-Development/rexedia">
        <img
            src="https://github-readme-stats.vercel.app/api/pin/?username=Ktt-Development&repo=rexedia&show_owner=true&title_color=3278be&text_color=202020">
    </a>
</div>

## ⚡ Recent Activity

 - Closed issue [Duplicate contexts do not throw IllegalArgumentException [EXTERNAL ISSUE] (#86)](https://github.com/Ktt-Development/simplehttpserver/issues/86) from repository [Ktt-Development/simplehttpserver](https://github.com/Ktt-Development/simplehttpserver)  *`1 hour ago`*
 - Commented on issue [Duplicate contexts do not throw IllegalArgumentException [EXTERNAL ISSUE] (#86)](https://github.com/Ktt-Development/simplehttpserver/issues/86#issuecomment-700357752) from repository [Ktt-Development/simplehttpserver](https://github.com/Ktt-Development/simplehttpserver)  *`1 hour ago`*
  > According to the source code an `IllegalArgumentException` is **never thrown** for duplicate contexts. The documentation on this method is invalid.
  >  > `sun.net.httpserver.ServerImpl`
  >  > ```java
  >  > ...
  >  >     public synchronized HttpContextImpl createContext (String path, HttpHandler handler) {
  >  >         if (handler == null || path == null) {
  >  >             throw new NullPointerException ("null handler, or path parameter");
  >  >         }
  >  >         HttpContextImpl context = new HttpContextImpl (protocol, path, handler, this);
  >  >         contexts.add (context);
  >  >         logger.log (Level.DEBUG, "context created: " + path);
  >  >         return context;
  >  >     }
  >  > ...
  >  > ```
  >  > `sun.net.httpserver.HttpContextImpl`
  >  > ```java
  >  > ...
  >  >     HttpContextImpl (String protocol, String path, HttpHandler cb, ServerImpl server) {
  >  >         if (path == null || protocol == null || path.length() < 1 || path.charAt(0) != '/') {
  >  >             throw new IllegalArgumentException ("Illegal value for path or protocol");
  >  >         }
  >  >         this.protocol = protocol.toLowerCase();
  >  >         this.path = path;
  >  >         if (!this.protocol.equals ("http") && !this.protocol.equals ("https")) {
  >  >             throw new IllegalArgumentException ("Illegal value for protocol");
  >  >         }
  >  >         this.handler = cb;
  >  >         this.server = server;
  >  >         authfilter = new AuthFilter(null);
  >  >         sfilters.add (authfilter);
  >  >     }
  >  > ...
  >  > ```
 - Closed issue [Can not remove extended HttpContext contexts [EXTERNAL ISSUE] (#87)](https://github.com/Ktt-Development/simplehttpserver/issues/87) from repository [Ktt-Development/simplehttpserver](https://github.com/Ktt-Development/simplehttpserver)  *`1 hour ago`*
 - Commented on issue [Can not remove extended HttpContext contexts [EXTERNAL ISSUE] (#87)](https://github.com/Ktt-Development/simplehttpserver/issues/87#issuecomment-700356595) from repository [Ktt-Development/simplehttpserver](https://github.com/Ktt-Development/simplehttpserver)  *`1 hour ago`*
  > `sun.net.httpserver.ServerImpl`
  >  > ```java
  >  > ...
  >  >     public synchronized void removeContext (HttpContext context) throws IllegalArgumentException {
  >  >         if (!(context instanceof HttpContextImpl)) {
  >  >                                         ^ here
  >  >             throw new IllegalArgumentException ("wrong HttpContext type");
  >  >         }
  >  >         contexts.remove ((HttpContextImpl)context);
  >  >         logger.log (Level.DEBUG, "context removed: " + context.getPath());
  >  >     }
  >  > ...
  >  > ```
 - Created branch [cleanup-and-optimizations@c8ab217](https://github.com/Katsute/Katsute/tree/cleanup-and-optimizations@c8ab217) in repository [Katsute/Katsute](https://github.com/Katsute/Katsute) *`1 hour ago`*

---
<img align="left" src="https://github.com/Katsute/Katsute/workflows/Update%20README.md/badge.svg"><p align="right">Last updated September 28, 2020 at 09:51 PM (EST)</p>
