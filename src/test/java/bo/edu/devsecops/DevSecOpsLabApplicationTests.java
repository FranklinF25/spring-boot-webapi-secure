package bo.edu.devsecops;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.httpBasic;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class DevSecOpsLabApplicationTests {

    @Autowired
    private MockMvc mockMvc;

    @Value("${lab.auth.username}")
    private String labUsername;

    @Value("${lab.auth.password}")
    private String labPassword;

    @Test
    void productSearchRejectsUnauthenticatedRequests() throws Exception {
        mockMvc.perform(get("/api/products/search").param("name", "Laptop"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void productSearchIsAvailableForAuthenticatedUser() throws Exception {
        mockMvc.perform(get("/api/products/search").param("name", "Laptop")
                        .with(httpBasic(labUsername, labPassword)))
                .andExpect(status().isOk());
    }

    @Test
    void adminEndpointRequiresAuthentication() throws Exception {
        mockMvc.perform(get("/api/admin/users/1"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void commentPreviewEscapesHtmlInResponse() throws Exception {
        mockMvc.perform(post("/api/comments/preview")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"comment\":\"<script>alert(1)</script>\"}"))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString("&lt;script&gt;")));
    }
}
