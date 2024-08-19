package dev.cyberaware.cyberawarebaseapp.screens

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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material3.Text
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.IconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.google.android.exoplayer2.ExoPlayer
import com.google.android.exoplayer2.MediaItem
import com.google.android.exoplayer2.Player
import com.google.android.exoplayer2.ui.AspectRatioFrameLayout
import com.google.android.exoplayer2.ui.StyledPlayerView
import java.util.logging.Logger

@Composable
fun BaseScreen(
    screenId: String,
    screenText: String,
    isImage: Boolean,
    resourceId: Int,
    buttons: List<@Composable (Modifier) -> Unit>
) {
    val context = LocalContext.current

    val isContentVisible = remember { mutableStateOf(isImage) }
    val videoUri = getUriFromRaw(context, rawResourceId = resourceId)

    Box(
        modifier = Modifier
            .fillMaxSize()
    ) {
        if (!isImage)
            VideoPlayer(uri = videoUri, isContentVisible = isContentVisible)
        else
            Image(
                painter = painterResource(id = resourceId),
                contentDescription = "Image",
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop
            )

        if (!isContentVisible.value)
            Box(modifier = Modifier
                .align(Alignment.TopEnd)
                .size(42.dp)
                .padding(8.dp)
                .background(
                    color = MaterialTheme.colorScheme.primary.copy(alpha = 0.5f),
                    shape = RoundedCornerShape(24.dp)
                )
                .clickable { },
            ) {
                IconButton(
                    onClick = { isContentVisible.value = !isContentVisible.value },
                ) {
                    Icon(imageVector = Icons.Default.Menu, contentDescription = "Show Content")
                }
            }

        if (isContentVisible.value) {
            Box(modifier = Modifier
                .align(Alignment.BottomCenter)
                .background(
                    color = MaterialTheme.colorScheme.surface.copy(alpha = 0.5f)
                )
                .clickable { },
            ) {
                if (isContentVisible.value)
                    Box(modifier = Modifier
                        .align(Alignment.TopEnd)
                        .size(42.dp)
                        .padding(8.dp)
                        .background(
                            color = MaterialTheme.colorScheme.primary,
                            shape = RoundedCornerShape(24.dp)
                        )
                        .clickable { },
                    ) {
                        IconButton(
                            onClick = { isContentVisible.value = !isContentVisible.value },
                        ) {
                            Icon(imageVector = Icons.Default.Close, contentDescription = "Hide Content")
                        }
                    }
                Column(
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(
                        text = screenText,
                        style = MaterialTheme.typography.bodyLarge,
                        modifier = Modifier
                            .padding(bottom = 16.dp, top = 28.dp)
                            .align(Alignment.Start)
                    )

                    Spacer(modifier = Modifier.weight(1f))

                    val buttonChunks = buttons.chunked(2)
                    buttonChunks.forEach { rowButtons ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            var i = 0
                            rowButtons.forEach { button ->
                                i++
                                button(Modifier.weight(1f))
                                if (i < rowButtons.size)
                                    Spacer(modifier = Modifier.width(16.dp))
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun OptionButton(modifier: Modifier, text: String, onNavigateToBaseScreen: () -> Unit) {
    Button(
        onClick = onNavigateToBaseScreen,
        colors = ButtonDefaults.buttonColors(
            contentColor = Color.White
        ),
        modifier = modifier
    ) {
        Text(text = text)
    }
}

@Composable
fun VideoPlayer(uri: Uri, isContentVisible: MutableState<Boolean>) {
    val context = LocalContext.current
    val exoPlayer = remember {
        ExoPlayer.Builder(context).build().apply {
            val mediaItem = MediaItem.fromUri(uri)
            setMediaItem(mediaItem)
            prepare()
            playWhenReady = true
        }
    }

    DisposableEffect(Unit) {
        val listener = object : Player.Listener {
            override fun onPlaybackStateChanged(playbackState: Int) {
                if (playbackState == Player.STATE_ENDED) {
                    isContentVisible.value = true
                }
            }
        }
        exoPlayer.addListener(listener)

        onDispose {
            exoPlayer.removeListener(listener)
            exoPlayer.release()
        }
    }

    AndroidView(
        factory = {
            StyledPlayerView(context).apply {
                player = exoPlayer
                resizeMode = AspectRatioFrameLayout.RESIZE_MODE_ZOOM
            }
        },
        modifier = Modifier.fillMaxSize()
    )
}

fun getUriFromRaw(context: Context, rawResourceId: Int): Uri {
    return Uri.parse("android.resource://${context.packageName}/$rawResourceId")
}
