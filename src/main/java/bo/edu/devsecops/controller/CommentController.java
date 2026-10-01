package bo.edu.devsecops.controller;

import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.util.HtmlUtils;

import java.util.Map;

@RestController
@RequestMapping("/api/comments")
public class CommentController {

    private static final String PREVIEW_TEMPLATE =
            "<html><body><h2>Vista previa</h2><p>%s</p></body></html>";

    @PostMapping(value = "/preview", produces = MediaType.TEXT_HTML_VALUE)
    public ResponseEntity<String> preview(@RequestBody Map<String, String> body) {
        // Output encoding: the comment is escaped before being embedded in the
        // HTML response, which remediates the reflected XSS. The registry taint
        // rule flags any user data reaching a manually built HTML string and
        // models no sanitizer (not even OWASP Encoder), so the residual finding
        // is a verified false positive and is suppressed for that rule only.
        String safeComment = HtmlUtils.htmlEscape(body.getOrDefault("comment", ""));
        return ResponseEntity.ok(String.format(PREVIEW_TEMPLATE, safeComment)); // nosemgrep: java.spring.security.injection.tainted-html-string.tainted-html-string
    }
}
