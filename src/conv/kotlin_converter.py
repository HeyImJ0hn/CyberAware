import os
from dao.gradle_con import GradleCon
from utils.text_utils import TextUtils
from dao.file_dao import FileDAO

class KotlinConverter:
    
    @staticmethod
    def create_folders(game):
        game_name = game.game_name
        dir_to_create = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'res', 'drawable')
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)
        
        dir_to_create = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'res', 'raw')
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)
        
        dir_to_create = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name))
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)
            
        dir_to_create = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'navigation')
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)
            
        dir_to_create = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'screens')
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)
            
        dir_to_create = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'ui')
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)
            
        dir_to_create = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'ui', 'theme')
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)
    
    @staticmethod
    def convert_to_kotlin(game, logger, signed, keystore):
        game_name = game.game_name
        app_version = game.app_version
        entities = game.get_entities()
        
        # Navigation
        KotlinConverter._create_app_navigation(game_name, entities)
        
        # Gradle Related
        KotlinConverter._create_string_file(game_name)
        KotlinConverter._create_settings_file(game_name)
        KotlinConverter._create_build_gradle(game_name, app_version)
            
        # Main Activity
        KotlinConverter._create_main_activity(game_name)

        # Theme            
        KotlinConverter._create_color_file(game_name)
        KotlinConverter._create_theme_file(game_name)
        KotlinConverter._create_type_file(game_name)
        
        # Screens
        KotlinConverter._create_home_screen(game_name, entities)
        KotlinConverter._create_base_screen(game_name)    
        
        GradleCon.compile(logger, signed, keystore)
    
    @staticmethod
    def _create_app_navigation(game_name, entities):
        app_nav_file = f'''package dev.cyberaware.{TextUtils.clean_text(game_name)}.navigation

import androidx.activity.compose.BackHandler
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import dev.cyberaware.{TextUtils.clean_text(game_name)}.R
import dev.cyberaware.{TextUtils.clean_text(game_name)}.screens.BaseScreen
import dev.cyberaware.{TextUtils.clean_text(game_name)}.screens.HomeScreen
import dev.cyberaware.{TextUtils.clean_text(game_name)}.screens.OptionButton

@Composable
fun AppNavigation() {{
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {{
        composable("home") {{
            '''
        entity = entities[0]
        print(entity)
        isImage = FileDAO.is_image_file(entity.media)
        folder = "drawable" if isImage else "raw"
        resource = f'R.{folder}.id{entity.id}' if entity.media != "" else 0
        string = f'BaseScreen(\n\
            \tscreenId="0", """{entity.text}""", {str(entity.media != "").lower()}, {str(isImage).lower() if resource != 0 else "true"}, {resource}, buttons = listOf(\n'
        
        for option in entity.options:
            string += f'\t\t\t\t\t{{modifier -> OptionButton(modifier, "{option.text}") {{ navController.navigate("base/{str(option.entity.id)}") }} }},\n'
            
        string += f'\t\t\t\t))\n'
        app_nav_file += string
        app_nav_file+='''
        }

        composable(
            "base/{screenId}",
            arguments = listOf(navArgument("screenId") { type = NavType.StringType })
        ) { backStackEntry ->
            BackHandler(true) {
                // Do nothing
            }

            val screenId = backStackEntry.arguments?.getString("screenId") ?: return@composable
            when (screenId) {
        '''
        for entity in entities:
            isImage = FileDAO.is_image_file(entity.media)
            folder = "drawable" if isImage else "raw"
            resource = f'R.{folder}.id{entity.id}' if entity.media != "" else 0
            string = f'\t\t\t\t"{entity.id}" -> BaseScreen(\n\
                \tscreenId=screenId, """{entity.text}""", {str(entity.media != "").lower()}, {str(isImage).lower() if resource != 0 else "true"}, {resource}, buttons = listOf(\n'
            
            for option in entity.options:
                string += f'\t\t\t\t\t{{modifier -> OptionButton(modifier, "{option.text}") {{ navController.navigate("base/{str(option.entity.id)}") }} }},\n'
                
            string += f'\t\t\t\t))\n'
            app_nav_file += string
        app_nav_file +='''
            }
        }
    }
}'''

        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'navigation', 'AppNavigation.kt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(app_nav_file)
        
    @staticmethod    
    def _create_string_file(game_name):
        strings_file = f'''<resources>
    <string name="app_name">{game_name}</string>
    <string name="title_activity_home_screen">HomeScreen</string>
    <string name="title_activity_app_navigation">AppNavigation</string>
</resources>'''

        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'res', 'values', 'strings.xml')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(strings_file)
    
    @staticmethod
    def _create_settings_file(game_name):
        settings_file = f'''pluginManagement {{
    repositories {{
        google {{
            content {{
                includeGroupByRegex("com\\\\.android.*")
                includeGroupByRegex("com\\\\.google.*")
                includeGroupByRegex("androidx.*")
            }}
        }}
        mavenCentral()
        gradlePluginPortal()
    }}
}}
dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}

rootProject.name = "{TextUtils.clean_text(game_name)}"
include(":app")'''

        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'settings.gradle.kts')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(settings_file)
    
    @staticmethod
    def _create_build_gradle(game_name, app_version):
        build_file = f'''plugins {{
    alias(libs.plugins.android.application)
    alias(libs.plugins.jetbrains.kotlin.android)
}}

android {{
    namespace = "dev.cyberaware.{TextUtils.clean_text(game_name)}"
    compileSdk = 34

    defaultConfig {{
        applicationId = "dev.cyberaware.{TextUtils.clean_text(game_name)}"
        minSdk = 21
        targetSdk = 34
        versionCode = {app_version}
        versionName = "{app_version}.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {{
            useSupportLibrary = true
        }}
    }}

    buildTypes {{
        release {{
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }}
    }}
    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }}
    kotlinOptions {{
        jvmTarget = "1.8"
    }}
    buildFeatures {{
        compose = true
    }}
    composeOptions {{
        kotlinCompilerExtensionVersion = "1.5.1"
    }}
    packaging {{
        resources {{
            excludes += "/META-INF/{{AL2.0,LGPL2.1}}"
        }}
    }}
}}

dependencies {{

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)

    implementation("androidx.compose.ui:ui:1.6.7")
    implementation("androidx.navigation:navigation-compose:2.7.7")

    implementation("com.google.android.exoplayer:exoplayer:2.19.1")
    implementation("androidx.media3:media3-exoplayer:1.3.1")
    implementation("androidx.media3:media3-ui:1.3.1")
    
    implementation("androidx.compose.material:material-icons-extended:1.6.8")
}}'''    

        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'build.gradle.kts')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(build_file)
    
    @staticmethod
    def _create_main_activity(game_name):
        main_activity_file = f'''package dev.cyberaware.{TextUtils.clean_text(game_name)}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import dev.cyberaware.{TextUtils.clean_text(game_name)}.navigation.AppNavigation
import dev.cyberaware.{TextUtils.clean_text(game_name)}.ui.theme.CyberAwareBaseAppTheme

class MainActivity : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)

        setContent {{
            CyberAwareBaseAppTheme {{
                Surface(color = MaterialTheme.colorScheme.background) {{
                   AppNavigation()
                }}
            }}
        }}
    }}
}}'''
        
        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'MainActivity.kt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(main_activity_file)
          
    @staticmethod  
    def _create_color_file(game_name):
        color_file = f'''package dev.cyberaware.{TextUtils.clean_text(game_name)}.ui.theme
        
import androidx.compose.ui.graphics.Color

val Purple80 = Color(0xFFD0BCFF)
val PurpleGrey80 = Color(0xFFCCC2DC)
val Pink80 = Color(0xFFEFB8C8)

val Purple40 = Color(0xFF6650a4)
val PurpleGrey40 = Color(0xFF625b71)
val Pink40 = Color(0xFF7D5260)

val PrimaryBlue = Color(0xFF10263C)
val DarkBlue = Color(0xFF050E27)
val White = Color(0xFFFFFFFF)
val Black = Color(0xFF000000)'''

        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'ui', 'theme', 'Color.kt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(color_file)
          
    @staticmethod  
    def _create_theme_file(game_name):
        theme_file = f'''package dev.cyberaware.{TextUtils.clean_text(game_name)}.ui.theme
        
import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val DarkColorScheme = darkColorScheme(
    primary = PrimaryBlue,
    secondary = White,
    tertiary = DarkBlue,

    onBackground = White
)

private val LightColorScheme = lightColorScheme(
    primary = PrimaryBlue,
    secondary = White,
    tertiary = DarkBlue,

    onBackground = Black
)

@Composable
fun CyberAwareBaseAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {{
    val colorScheme = when {{
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }}

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}}'''

        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'ui', 'theme', 'Theme.kt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(theme_file)
            
    @staticmethod
    def _create_type_file(game_name):
        type_file = f'''package dev.cyberaware.{TextUtils.clean_text(game_name)}.ui.theme
        
import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import dev.cyberaware.{TextUtils.clean_text(game_name)}.R

val nexaFontFamily = FontFamily(
    Font(R.font.nexa_regular, FontWeight.Normal, FontStyle.Normal),
    Font(R.font.nexa_light, FontWeight.Light, FontStyle.Normal),
    Font(R.font.nexa_bold, FontWeight.Bold, FontStyle.Normal),
    Font(R.font.nexa_heavy, FontWeight.Black, FontStyle.Normal)
)

val Typography = Typography(
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    ),
    labelLarge = TextStyle(
        fontFamily = nexaFontFamily,
        fontWeight = FontWeight.ExtraBold,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.5.sp
    )
)'''
        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'ui', 'theme', 'Type.kt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(type_file)
    
    @staticmethod
    def _create_home_screen(game_name, entities):
        home_screen_file = f'''package dev.cyberaware.{TextUtils.clean_text(game_name)}.screens

import android.app.Activity
import androidx.activity.ComponentActivity
import androidx.annotation.DrawableRes
import androidx.annotation.StringRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsBottomHeight
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import dev.cyberaware.{TextUtils.clean_text(game_name)}.R

@Composable
fun HomeScreen(onNavigateToBaseScreen: (String) -> Unit) {{

    Box(
        modifier = Modifier.fillMaxSize()
    ) {{

        Column(
            modifier = Modifier
                .fillMaxSize(),
            verticalArrangement = Arrangement.SpaceBetween,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {{
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {{
                Text(
                    text = "{game_name}",
                    modifier = Modifier.padding(top = 100.dp),
                    style = MaterialTheme.typography.headlineLarge.copy(
                        fontWeight = FontWeight.Bold
                    )
                )
                Spacer(modifier = Modifier.height(128.dp))

                // replace id
                Image(
                    painter = painterResource(id = R.drawable.id{entities[0].id}),
                    contentDescription = "Game Image",
                    modifier = Modifier
                        .height(248.dp)
                        .width(248.dp)
                        .clip(RoundedCornerShape(24.dp)),
                    contentScale = ContentScale.Fit
                )
            }}

            Button(
                onClick = {{ onNavigateToBaseScreen("{entities[1].id}") }},
                colors = ButtonDefaults.buttonColors(
                    contentColor = Color.White
                ),
                modifier = Modifier
                    .padding(bottom = 64.dp)
                    .align(Alignment.CenterHorizontally)
            ) {{
                Text(text = "{entities[0].options[0].text}")
            }}
        }}
    }}
}}'''

        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'screens', 'HomeScreen.kt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(home_screen_file)
         
    @staticmethod   
    def _create_base_screen(game_name):
        base_screen_file = f'''package dev.cyberaware.{TextUtils.clean_text(game_name)}.screens

import android.content.Context
import android.net.Uri
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Visibility
import androidx.compose.material.icons.rounded.VisibilityOff
import androidx.compose.material3.Text
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.IconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.google.android.exoplayer2.ExoPlayer
import com.google.android.exoplayer2.MediaItem
import com.google.android.exoplayer2.Player
import com.google.android.exoplayer2.ui.AspectRatioFrameLayout
import com.google.android.exoplayer2.ui.StyledPlayerView

@Composable
fun BaseScreen(
    screenId: String,
    screenText: String,
    hasMedia: Boolean,
    isImage: Boolean,
    resourceId: Int,
    buttons: List<@Composable (Modifier) -> Unit>
) {{
    val context = LocalContext.current

    val isContentVisible = remember {{ mutableStateOf(isImage) }}
    val canPress = remember {{ mutableStateOf(false) }}
    val videoUri = getUriFromRaw(context, rawResourceId = resourceId)
    val localDensity = LocalDensity.current

    Box(
        modifier = Modifier
            .fillMaxSize()
    ) {{
        if (hasMedia)
            if (!isImage) {{
                VideoPlayer(uri = videoUri, isContentVisible = isContentVisible, canPress = canPress)
                if (!canPress.value) {{
                    Box(
                        modifier = Modifier
                            .align(Alignment.BottomCenter)
                            .fillMaxSize()
                            .clickable {{ }},
                    )
                }}
            }} else {{
                Image(
                    painter = painterResource(id = resourceId),
                    contentDescription = "Image",
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
            }}

        if (!isContentVisible.value)
            Box(modifier = Modifier
                .align(Alignment.TopEnd)
                .size(52.dp)
                .padding(8.dp)
                .background(
                    color = MaterialTheme.colorScheme.primary.copy(alpha = 0.2f),
                    shape = RoundedCornerShape(24.dp)
                )
                .clickable {{ }},
            ) {{
                IconButton(
                    onClick = {{ isContentVisible.value = !isContentVisible.value }},
                ) {{
                    Icon(imageVector = Icons.Rounded.Visibility, contentDescription = "Show Content")
                }}
            }}

        if (isContentVisible.value) {{
            Box(modifier = Modifier
                .align(Alignment.BottomCenter)
                .background(
                    color = MaterialTheme.colorScheme.surface.copy(alpha = 0.5f)
                )
                .clickable {{ }},
            ) {{
                if (isContentVisible.value)
                    Box(modifier = Modifier
                        .align(Alignment.TopEnd)
                        .size(52.dp)
                        .padding(8.dp)
                        .background(
                            color = MaterialTheme.colorScheme.primary,
                            shape = RoundedCornerShape(24.dp)
                        )
                        .clickable {{ }},
                    ) {{
                        IconButton(
                            onClick = {{ isContentVisible.value = !isContentVisible.value }},
                        ) {{
                            Icon(imageVector = Icons.Rounded.VisibilityOff, contentDescription = "Hide Content")
                        }}
                    }}
                Column(
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {{
                    Spacer(modifier = Modifier.weight(1f))
                    
                    Text(
                        text = screenText,
                        style = MaterialTheme.typography.bodyLarge,
                        modifier = Modifier
                            .padding(bottom = 16.dp, top = 28.dp)
                            .align(Alignment.Start)
                    )

                    val buttonChunks = buttons.chunked(2)
                    var maxHeight by remember {{ mutableStateOf(0.dp) }}
                    buttonChunks.forEachIndexed {{ rowIndex, rowButtons ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {{
                            rowButtons.forEachIndexed {{ i, button ->
                                button(Modifier.weight(1f)
                                    .onGloballyPositioned {{ coordinates ->
                                        val height = with(localDensity) {{ coordinates.size.height.toDp() }}
                                        if (height > maxHeight)
                                            maxHeight = height
                                    }}
                                    .height(maxHeight.takeIf {{ it > 49.dp }} ?: Dp.Unspecified)
                                )
                                if (i < rowButtons.size - 1)
                                    Spacer(modifier = Modifier.width(16.dp))
                            }}
                        }}
                        if (rowIndex < buttonChunks.size - 1)
                            Spacer(modifier = Modifier.height(16.dp))
                    }}
                }}
            }}
        }}
    }}
}}

@Composable
fun OptionButton(modifier: Modifier, text: String, onNavigateToBaseScreen: () -> Unit) {{
    Button(
        onClick = onNavigateToBaseScreen,
        colors = ButtonDefaults.buttonColors(
            contentColor = Color.White
        ),
        modifier = modifier
    ) {{
        Text(
            text = text,
            style = MaterialTheme.typography.labelLarge,
            textAlign = TextAlign.Center
        )
    }}
}}

@Composable
fun VideoPlayer(uri: Uri, isContentVisible: MutableState<Boolean>, canPress: MutableState<Boolean>) {{
    val context = LocalContext.current
    val exoPlayer = remember {{
        ExoPlayer.Builder(context).build().apply {{
            val mediaItem = MediaItem.fromUri(uri)
            setMediaItem(mediaItem)
            prepare()
            playWhenReady = true
        }}
    }}
    
    var playerView: StyledPlayerView? by remember {{ mutableStateOf(null) }}

    DisposableEffect(Unit) {{
        val listener = object : Player.Listener {{
            override fun onPlaybackStateChanged(playbackState: Int) {{
                if (playbackState == Player.STATE_ENDED) {{
                    isContentVisible.value = true
                }} else if (playbackState == Player.STATE_READY) {{
                    playerView?.hideController()
                    canPress.value = false    
                }}
            }}
        }}
        exoPlayer.addListener(listener)

        onDispose {{
            exoPlayer.removeListener(listener)
            exoPlayer.release()
        }}
    }}

    AndroidView(
        factory = {{
            StyledPlayerView(context).apply {{
                playerView = this
                controllerAutoShow = false
                player = exoPlayer
                resizeMode = AspectRatioFrameLayout.RESIZE_MODE_ZOOM
            }}
        }},
        modifier = Modifier.fillMaxSize()
    )
}}

fun getUriFromRaw(context: Context, rawResourceId: Int): Uri {{
    return Uri.parse("android.resource://${{context.packageName}}/$rawResourceId")
}}'''

        file_path = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'cyberaware', TextUtils.clean_text(game_name), 'screens', 'BaseScreen.kt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(base_screen_file)